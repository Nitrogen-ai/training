#!/usr/bin/env python3
"""Zeichnet in bereits exportierten Skelettformel-SVGs des Chemical Communication Trainers die
symmetrischen Doppelbindungen (zwei gleich lange Linien, ±0,13 Bindungslängen) im neuen Stil um:
Achsenlinie + um 0,16 versetzte, an inneren Enden um 18 % gekürzte Zweitlinie (Ring: zur Ringmitte,
Kette: zur Seite der Nachbarbindungen, Gleichstand: nach unten). C=O/C=S mit freiem beschrifteten
Endatom bleibt zentriert. Alles andere (Zuschnitt, Farben, Texte) bleibt unverändert.

Aufruf: python3 doppelbindungen_umzeichnen.py [--dry] datei.svg ...
Die Bindungslänge wird aus dem Abstand der Doppelbindungslinien abgeleitet (±0,13 Bindungslängen, wie im Trainer).
"""
import math, re, sys

LINE = re.compile(r'<line x1="([-\d.]+)" y1="([-\d.]+)" x2="([-\d.]+)" y2="([-\d.]+)"([^>]*?)/>')
TEXT = re.compile(r'<text x="([-\d.]+)" y="([-\d.]+)"[^>]*>([^<]*)</text>')

def umzeichnen(svg):
    lines = [dict(m=m, p=(float(m[1]), float(m[2])), q=(float(m[3]), float(m[4])), rest=m[5]) for m in LINE.finditer(svg)]
    texts = [(float(m[1]), float(m[2]), m[3]) for m in TEXT.finditer(svg) if m[3].strip() and m[3].strip() not in '+−-2−' ]
    if not lines: return svg, 0
    d = lambda a, b: math.hypot(a[0] - b[0], a[1] - b[1])
    # Kandidaten: zwei gleich lange, parallele, nur senkrecht gegeneinander versetzte Linien
    def partner(a, b):
        la, lb = d(a['p'], a['q']), d(b['p'], b['q'])
        if la < 1 or abs(la - lb) > 0.01 * la: return None
        ux, uy = (a['q'][0] - a['p'][0]) / la, (a['q'][1] - a['p'][1]) / la
        for bp, bq in ((b['p'], b['q']), (b['q'], b['p'])):
            vp = (bp[0] - a['p'][0], bp[1] - a['p'][1]); vq = (bq[0] - a['q'][0], bq[1] - a['q'][1])
            if 0.1 * la < d(vp, (0, 0)) < 0.5 * la and d(vp, vq) < 0.005 * la + 0.05 and abs(vp[0] * ux + vp[1] * uy) < 0.005 * la + 0.05:
                return True
        return None
    # Dreifachbindungen (Linie mit zwei Partnern) vorab ausschließen
    used = set()
    for i, a in enumerate(lines):
        ps = [j for j, b in enumerate(lines) if j != i and partner(a, b)]
        if len(ps) >= 2: used |= {i, *ps}
    cand = []
    for i, a in enumerate(lines):
        for j in range(i + 1, len(lines)):
            if i in used or j in used: continue
            b = lines[j]
            la, lb = d(a['p'], a['q']), d(b['p'], b['q'])
            if la < 1 or abs(la - lb) > 0.01 * la: continue
            ux, uy = (a['q'][0] - a['p'][0]) / la, (a['q'][1] - a['p'][1]) / la
            for bp, bq in ((b['p'], b['q']), (b['q'], b['p'])):
                vp = (bp[0] - a['p'][0], bp[1] - a['p'][1]); vq = (bq[0] - a['q'][0], bq[1] - a['q'][1])
                sep = d(vp, (0, 0))
                if 0.1 * la < sep < 0.5 * la and d(vp, vq) < 0.005 * la + 0.05 and abs(vp[0] * ux + vp[1] * uy) < 0.005 * la + 0.05:
                    P = ((a['p'][0] + bp[0]) / 2, (a['p'][1] + bp[1]) / 2); Q = ((a['q'][0] + bq[0]) / 2, (a['q'][1] + bq[1]) / 2)
                    cand.append((i, j, P, Q, sep)); used |= {i, j}
                    break
    if not cand: return svg, 0
    seps = sorted(c[4] for c in cand)
    L = seps[len(seps) // 2] / 0.26  # Bindungslänge: Doppelbindungslinien liegen ±0,13 L
    tol = 0.06 * L
    pairs = [c[:4] for c in cand if abs(c[4] - 0.26 * L) < 0.03 * L]
    used = {k for c in pairs for k in c[:2]}
    if not pairs: return svg, 0
    # Graph: Knoten = Linienenden (versteckte C) und Beschriftungen
    nodes = []
    def node(pt):
        for k, n in enumerate(nodes):
            if d(n, pt) < tol: return k
        nodes.append(pt); return len(nodes) - 1
    lab = {}
    def endnode(pt, other):
        # Linienende an einer Beschriftung? (Bindung endet labelPad = 0,22 L vor der Atommitte)
        u = (pt[0] - other[0], pt[1] - other[1]); n = math.hypot(*u) or 1
        c = (pt[0] + u[0] / n * 0.22 * L, pt[1] + u[1] / n * 0.22 * L)
        for t in texts:
            if d((t[0], t[1]), c) < 0.12 * L:
                key = (round(t[0], 1), round(t[1], 1))
                if key not in lab: lab[key] = node((t[0], t[1]))
                return lab[key], True
        return node(pt), False
    edges = []
    segs = [(k, l['p'], l['q']) for k, l in enumerate(lines) if k not in used] + [(-1 - n, P, Q) for n, (i, j, P, Q) in enumerate(pairs)]
    info = {}
    for k, p, q in segs:
        a, la_ = endnode(p, q); b, lb_ = endnode(q, p)
        edges.append((a, b)); info[k] = (a, la_, b, lb_)
    adj = {}
    for a, b in edges: adj.setdefault(a, []).append(b); adj.setdefault(b, []).append(a)
    def ring(s, t):
        prev = {s: None}; q = [s]
        for _ in range(7):
            nq = []
            for u in q:
                for v in adj.get(u, []):
                    if (u == s and v == t) or v in prev: continue
                    prev[v] = u
                    if v == t:
                        path = []; w = t
                        while w is not None: path.append(w); w = prev[w]
                        return path
                    nq.append(v)
            q = nq
        return None
    out = {}
    n_done = 0
    for n, (i, j, P, Q) in enumerate(pairs):
        a, labA, b, labB = info[-1 - n]
        if (labA and len(adj[a]) == 1) or (labB and len(adj[b]) == 1): continue  # =O zentriert lassen
        A, B = nodes[a], nodes[b]
        ux, uy = Q[0] - P[0], Q[1] - P[1]; l = math.hypot(ux, uy); ux, uy = ux / l, uy / l
        nx, ny = -(B[1] - A[1]), B[0] - A[0]; nl = math.hypot(nx, ny); nx, ny = nx / nl, ny / nl
        r = ring(a, b); score = 0
        if r:
            cx = sum(nodes[k][0] for k in r) / len(r); cy = sum(nodes[k][1] for k in r) / len(r)
            score = (cx - (A[0] + B[0]) / 2) * nx + (cy - (A[1] + B[1]) / 2) * ny
        else:
            for x, y in ((a, b), (b, a)):
                for k in adj[x]:
                    if k == y: continue
                    kx, ky = nodes[k][0] - nodes[x][0], nodes[k][1] - nodes[x][1]; kl = math.hypot(kx, ky) or 1
                    score += (kx * nx + ky * ny) / kl
        if abs(score) < 0.02: score = ny if abs(ny) > 1e-9 else nx  # Gleichstand: nach unten
        sd = 1 if score > 0 else -1
        off = 0.16 * L
        inA = 0 if (labA or len(adj[a]) == 1) else 0.18 * d(A, B)
        inB = 0 if (labB or len(adj[b]) == 1) else 0.18 * d(A, B)
        p1 = (P[0] + ux * inA + nx * off * sd, P[1] + uy * inA + ny * off * sd)
        q1 = (Q[0] - ux * inB + nx * off * sd, Q[1] - uy * inB + ny * off * sd)
        fmt = lambda p, q, rest: f'<line x1="{p[0]:.2f}" y1="{p[1]:.2f}" x2="{q[0]:.2f}" y2="{q[1]:.2f}"{rest}/>'
        out[i] = fmt(P, Q, lines[i]['rest']); out[j] = fmt(p1, q1, lines[j]['rest'])
        n_done += 1
    if not out: return svg, 0
    res, last = [], 0
    for k, l in enumerate(lines):
        if k in out:
            res.append(svg[last:l['m'].start()]); res.append(out[k]); last = l['m'].end()
    res.append(svg[last:])
    return ''.join(res), n_done

if __name__ == '__main__':
    dry = '--dry' in sys.argv
    for f in [a for a in sys.argv[1:] if a != '--dry']:
        s = open(f, encoding='utf-8').read()
        t, n = umzeichnen(s)
        print(f'{n:2d} Doppelbindung(en)  {f}')
        if n and not dry: open(f, 'w', encoding='utf-8').write(t)
