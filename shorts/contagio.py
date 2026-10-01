"""Contagio: palline di squadre diverse; a ogni scontro una converte l'altra.

Fase 2 ("THE WALL BREAKS"): nell'anello si apre un varco rotante e chi esce
è fuori. Senza questo il duello finale sarebbe un random walk lunghissimo.

La simulazione è deterministica dato il seed. Si simulano molti seed senza
renderizzare, si calcola un "drama score" e si renderizza solo il migliore.
"""

from dataclasses import dataclass, field

import numpy as np

W, H = 1080, 1920
CENTER = np.array([540.0, 1010.0])
ARENA_R = 440.0
BALL_R = 36.0
PER_TEAM = 4
SUBSTEPS_PER_SEC = 240
BASE_SPEED = 470.0
IMMUNITY = 0.3  # secondi in cui una pallina appena convertita non può essere riconvertita
# Probabilità che uno scontro converta: bassa all'inizio, piena quando il muro si rompe.
CONVERT_P = 0.3
CONVERT_P_FINAL = 1.0

# Eventi caos programmati (tempo simulazione). Il render mostra un banner per ognuno.
SCHEDULE = [
    (8.5, "speed", 1.45, "SPEED UP!"),
    (15.0, "gravity", 1300.0, "GRAVITY ON"),
    (20.0, "gravity", -1300.0, "GRAVITY FLIP!"),
    (24.5, "gap", None, "THE WALL BREAKS!"),
]
GAP_SPIN = 0.9                  # rad/s
GAP_OPEN = (0.0, np.radians(22))
GAP_WIDEN_TO = np.radians(58)
GAP_WIDEN_TIME = 8.0

# Finestra in cui deve arrivare il vincitore perché il video duri ~40s.
END_MIN, END_MAX = 32.8, 34.3
TAIL = 7.0  # secondi di simulazione extra dopo la vittoria (slow-mo + festa)

IN_PLAY, ESCAPING, GONE = 0, 1, 2


@dataclass
class Record:
    seed: int
    n_teams: int
    dt: float
    pos: np.ndarray | None      # (steps, N, 2) float32
    team: np.ndarray | None     # (steps, N) int8
    state: np.ndarray | None    # (steps, N) int8: IN_PLAY / ESCAPING / GONE
    gap: np.ndarray | None      # (steps, 2) centro e semi-ampiezza del varco (rad)
    counts: np.ndarray          # (steps, n_teams)
    conversions: list = field(default_factory=list)   # (t, x, y, winner, loser, ball)
    escapes: list = field(default_factory=list)       # (t, ball, team, x, y)
    eliminations: list = field(default_factory=list)  # (t, team, x, y)
    events: list = field(default_factory=list)        # (t, kind, label)
    t_end: float | None = None
    winner: int | None = None
    final_hit: tuple | None = None                    # (t, x, y)


def simulate(seed, n_teams, duration=END_MAX + TAIL, record=True):
    rng = np.random.default_rng(seed)
    n = n_teams * PER_TEAM
    dt = 1.0 / SUBSTEPS_PER_SEC
    steps = int(duration * SUBSTEPS_PER_SEC)

    # Posizioni iniziali casuali senza sovrapposizioni.
    pos = np.zeros((n, 2))
    placed = 0
    while placed < n:
        a = rng.uniform(0, 2 * np.pi)
        rr = np.sqrt(rng.uniform(0, 1)) * (ARENA_R - BALL_R - 4)
        cand = CENTER + rr * np.array([np.cos(a), np.sin(a)])
        if placed == 0 or np.min(np.linalg.norm(pos[:placed] - cand, axis=1)) > 2 * BALL_R + 6:
            pos[placed] = cand
            placed += 1
    ang = rng.uniform(0, 2 * np.pi, n)
    vel = np.stack([np.cos(ang), np.sin(ang)], axis=1) * BASE_SPEED
    team = np.repeat(np.arange(n_teams), PER_TEAM)
    rng.shuffle(team)
    state = np.zeros(n, np.int8)
    immune_until = np.zeros(n)
    counts = np.bincount(team, minlength=n_teams)

    min_d2 = (2 * BALL_R) ** 2
    speed_mult = 1.0
    convert_p = CONVERT_P
    gravity = 0.0
    gap_t0 = None
    gap_angle = rng.uniform(0, 2 * np.pi)
    sched = list(SCHEDULE)

    rec = Record(
        seed=seed, n_teams=n_teams, dt=dt,
        pos=np.zeros((steps, n, 2), np.float32) if record else None,
        team=np.zeros((steps, n), np.int8) if record else None,
        state=np.zeros((steps, n), np.int8) if record else None,
        gap=np.zeros((steps, 2), np.float32) if record else None,
        counts=np.zeros((steps, n_teams), np.int16),
    )

    def remove(ball, t, x, y):
        """Toglie una pallina dal conteggio (conversione o fuga) e controlla eliminazioni/vittoria."""
        lt = team[ball]
        counts[lt] -= 1
        if counts[lt] == 0:
            rec.eliminations.append((t, int(lt), x, y))
            alive = int((counts > 0).sum())
            if alive == 2:
                rec.events.append((t, "duel", "FINAL DUEL"))
            if alive <= 1 and rec.t_end is None:
                rec.t_end = t
                rec.winner = int(np.argmax(counts)) if alive == 1 else int(lt)
                rec.final_hit = (t, x, y)

    for s in range(steps):
        t = s * dt

        while sched and t >= sched[0][0]:
            et, kind, val, label = sched.pop(0)
            if kind == "speed":
                speed_mult = val
            elif kind == "gravity":
                gravity = val
            elif kind == "gap":
                gravity = 0.0
                gap_t0 = et
                convert_p = CONVERT_P_FINAL
            if rec.t_end is None:
                rec.events.append((et, kind, label))

        # Varco: si apre, ruota, si allarga; dopo la vittoria si richiude.
        gap_half = 0.0
        if gap_t0 is not None:
            gap_angle += GAP_SPIN * dt
            k = t - gap_t0
            gap_half = GAP_OPEN[1] * min(1.0, k / 0.6)
            gap_half += (GAP_WIDEN_TO - GAP_OPEN[1]) * min(1.0, max(0.0, (k - 0.6) / GAP_WIDEN_TIME))
            if rec.t_end is not None:
                gap_half *= max(0.0, 1.0 - (t - rec.t_end) / 0.5)

        play = state == IN_PLAY
        # Velocità costante: la gravità curva solo la traiettoria.
        if gravity:
            vel[play, 1] += gravity * dt
        sp = np.linalg.norm(vel, axis=1, keepdims=True) + 1e-9
        vel[play] *= (BASE_SPEED * speed_mult) / sp[play]
        # Piccolo rumore angolare per evitare orbite periodiche.
        jitter = rng.normal(0, 0.004, n)
        c, sn = np.cos(jitter), np.sin(jitter)
        vel = np.stack([vel[:, 0] * c - vel[:, 1] * sn, vel[:, 0] * sn + vel[:, 1] * c], axis=1)
        pos += vel * dt

        # Muro circolare (con varco).
        d = pos - CENTER
        dist = np.linalg.norm(d, axis=1)
        lim = ARENA_R - BALL_R
        for b in np.nonzero((dist > lim) & play)[0]:
            nrm = d[b] / dist[b]
            if gap_half > 0:
                a = np.arctan2(nrm[1], nrm[0])
                off = (a - gap_angle + np.pi) % (2 * np.pi) - np.pi
                if abs(off) < gap_half - 0.5 * BALL_R / ARENA_R:
                    state[b] = ESCAPING
                    rec.escapes.append((t, int(b), int(team[b]), pos[b, 0], pos[b, 1]))
                    remove(b, t, pos[b, 0], pos[b, 1])
                    continue
            pos[b] = CENTER + nrm * lim
            vn = vel[b] @ nrm
            if vn > 0:
                vel[b] -= 2 * vn * nrm
        state[(state == ESCAPING) & (dist > 1400)] = GONE

        # Urti tra palline in gioco.
        idx = np.nonzero(state == IN_PLAY)[0]
        if len(idx) > 1:
            I, J = np.triu_indices(len(idx), 1)
            diff = pos[idx[I]] - pos[idx[J]]
            d2 = np.einsum("ij,ij->i", diff, diff)
            for k in np.nonzero(d2 < min_d2)[0]:
                i, j = idx[I[k]], idx[J[k]]
                dd = pos[i] - pos[j]
                dist_ij = np.sqrt(dd @ dd) + 1e-9
                nrm = dd / dist_ij
                overlap = 2 * BALL_R - dist_ij
                pos[i] += nrm * overlap / 2
                pos[j] -= nrm * overlap / 2
                vn = (vel[i] - vel[j]) @ nrm
                if vn >= 0:
                    continue
                vel[i] -= vn * nrm
                vel[j] += vn * nrm
                if team[i] == team[j] or rec.t_end is not None:
                    continue
                if t < immune_until[i] or t < immune_until[j]:
                    continue
                if rng.random() > convert_p:
                    continue
                w, l = (i, j) if rng.random() < 0.5 else (j, i)
                hit = (pos[i] + pos[j]) / 2
                rec.conversions.append((t, hit[0], hit[1], int(team[w]), int(team[l]), int(l)))
                remove(l, t, hit[0], hit[1])
                team[l] = team[w]
                counts[team[w]] += 1
                immune_until[l] = t + IMMUNITY
                if rec.t_end == t:  # la conversione ha chiuso la partita
                    rec.winner = int(team[w])

        rec.counts[s] = counts
        if record:
            rec.pos[s] = pos
            rec.team[s] = team
            rec.state[s] = state
            rec.gap[s] = (gap_angle, gap_half)
        elif rec.t_end is not None:
            rec.counts = rec.counts[: s + 1]
            break

    return rec


def drama_score(rec):
    """Più è alto, più la partita è da vedere. None se fuori finestra."""
    if rec.t_end is None or not (END_MIN <= rec.t_end <= END_MAX):
        return None
    dt = rec.dt
    counts = rec.counts
    end_step = int(rec.t_end / dt)
    q = SUBSTEPS_PER_SEC // 4
    sample = counts[:end_step:q]  # 4 campioni/sec

    # Cambi di leader (solo se il nuovo leader è davanti in modo netto).
    leader, changes = None, 0
    for row in sample[12:]:
        top = int(np.argmax(row))
        if leader is None:
            leader = top
        elif top != leader and row[top] > row[leader]:
            leader = top
            changes += 1

    w = rec.winner
    after = counts[int(8 / dt): end_step, w]
    winner_min = int(after.min()) if len(after) else PER_TEAM
    s15 = int(15 / dt)
    rank15 = int((counts[s15] > counts[s15, w]).sum())

    elim_times = [0.0] + [e[0] for e in rec.eliminations]
    max_quiet = max(np.diff(elim_times)) if len(elim_times) > 1 else rec.t_end
    duel_start = elim_times[-2] if len(elim_times) >= 3 else 0.0
    duel_len = rec.t_end - duel_start
    alive_at_gap = int((counts[int(SCHEDULE[-1][0] / dt)] > 0).sum())

    # Nel duello: quante volte il comando passa di mano.
    duel_changes = 0
    if duel_len > 0:
        seg = counts[int(duel_start / dt) + 1: end_step: q]
        alive = [int(x) for x in np.nonzero(seg[0])[0]] if len(seg) else []
        if len(alive) == 2:
            a, b = alive
            sign = np.sign(seg[:, a].astype(int) - seg[:, b].astype(int))
            sign = sign[sign != 0]
            duel_changes = int((np.diff(sign) != 0).sum())

    score = min(changes, 14) * 1.0
    score += 6.0 if winner_min <= 2 else 0.0
    score += 4.0 if winner_min <= 1 else 0.0
    score += 3.0 if rank15 >= 3 else 0.0
    score += 4.0 if 3.0 <= duel_len <= 9.0 else (-4.0 if duel_len > 14 else 0.0)
    score += min(duel_changes, 6) * 1.5
    score += 3.0 if alive_at_gap >= 3 else 0.0
    score -= max(0.0, max_quiet - 8.0) * 1.5
    return {
        "score": round(float(score), 2), "lead_changes": changes, "winner_min": winner_min,
        "winner_rank_at_15s": rank15 + 1, "duel_len": round(float(duel_len), 2),
        "duel_changes": duel_changes, "alive_at_gap": alive_at_gap,
        "max_quiet": round(float(max_quiet), 2), "t_end": round(float(rec.t_end), 2), "winner": w,
    }


def _eval(args):
    seed, n_teams = args
    rec = simulate(seed, n_teams, record=False)
    return seed, (rec.t_end, drama_score(rec))


def search(n_teams, seeds, workers=None):
    import os
    from multiprocessing import Pool
    with Pool(workers or os.cpu_count() or 1) as pool:
        return pool.map(_eval, [(s, n_teams) for s in seeds], chunksize=4)
