import numpy as np
import plotly.graph_objects as go


def _as_points(points, dim=None):
    pts = np.asarray(points, dtype=float)
    if pts.ndim == 1:
        pts = pts.reshape(-1, 1)
    if pts.ndim != 2 or len(pts) == 0:
        raise ValueError("path must be a non-empty list of points")
    if dim is not None and pts.shape[1] != dim:
        raise ValueError(f"expected points with {dim} coordinate(s), got {pts.shape[1]}")
    return pts


def _frame_indices(n, max_frames):
    if n <= max_frames:
        return np.arange(n)
    return np.unique(np.linspace(0, n - 1, max_frames).round().astype(int))


def _animation_controls(indices, duration=300):
    play = dict(frame=dict(duration=duration, redraw=True), fromcurrent=True)
    pause = dict(frame=dict(duration=0), mode="immediate")
    return dict(
        updatemenus=[dict(
            type="buttons", direction="left", x=0.05, y=0, xanchor="left", yanchor="top",
            buttons=[dict(label="▶ Play", method="animate", args=[None, play]),
                     dict(label="⏸ Pause", method="animate", args=[[None], pause])],
        )],
        sliders=[dict(
            x=0.2, y=0, len=0.75, xanchor="left", yanchor="top",
            currentvalue=dict(prefix="Iteration: "),
            steps=[dict(label=str(k), method="animate",
                        args=[[str(k)], dict(mode="immediate", frame=dict(duration=0, redraw=True))])
                   for k in indices],
        )],
    )


def _add_animation(fig, path_trace, end_trace, n, trace_ids, max_frames):
    idx = _frame_indices(n, max_frames)
    fig.frames = [go.Frame(name=str(k), data=[path_trace(k), end_trace(k)], traces=trace_ids)
                  for k in idx]
    fig.update_layout(**_animation_controls(idx))


def _axis(values, margin, size):
    pad = np.ptp(values) * margin or 1.0
    return np.linspace(values.min() - pad, values.max() + pad, size)


def plot_path_1d(f, points, animate=False, margin=0.3, grid_size=300, show=True, max_frames=200):
    pts = _as_points(points, 1)
    xs = pts[:, 0]
    fs = np.array([f(x) for x in xs], dtype=float)
    n = len(xs)

    gx = _axis(xs, margin, grid_size)
    gf = np.array([f(x) for x in gx], dtype=float)

    lo, hi = min(np.nanmin(gf), np.nanmin(fs)), max(np.nanmax(gf), np.nanmax(fs))
    pad = (hi - lo) * 0.05 or 1.0

    curve = go.Scatter(x=gx, y=gf, mode="lines", line=dict(color="royalblue", width=2),
                       name="f(x)", hoverinfo="skip")
    hover = "x=%{x:.4f}<br>f=%{y:.4f}<extra></extra>"

    def path_trace(k):
        return go.Scatter(x=xs[:k + 1], y=fs[:k + 1], mode="lines+markers",
                          line=dict(color="black", width=2), marker=dict(size=6, color="black"),
                          name="trajectory", hovertemplate=hover)

    def end_trace(k):
        return go.Scatter(x=[xs[k]], y=[fs[k]], mode="markers+text",
                          marker=dict(size=14, color="red"),
                          text=[f"f = {fs[k]:.4g}"], textposition="top center",
                          name="end", hovertemplate=hover)

    start = go.Scatter(x=[xs[0]], y=[fs[0]], mode="markers",
                       marker=dict(size=14, color="blue"), name="start", hovertemplate=hover)

    k0 = 0 if animate else n - 1
    fig = go.Figure(data=[curve, path_trace(k0), start, end_trace(k0)])
    if animate:
        _add_animation(fig, path_trace, end_trace, n, [1, 3], max_frames)

    fig.update_layout(xaxis=dict(title="x", range=[gx[0], gx[-1]]),
                      yaxis=dict(title="f(x)", range=[lo - pad, hi + pad]),
                      margin=dict(l=40, r=20, t=30, b=40), legend=dict(x=1.02, y=1))
    if show:
        fig.show()
    return fig


def plot_path_2d(f, points, animate=False, margin=0.3, grid_size=60, show=True, max_frames=200):
    pts = _as_points(points, 2)
    xs, ys = pts[:, 0], pts[:, 1]
    zs = np.array([f(x, y) for x, y in pts], dtype=float)
    n = len(pts)

    gx, gy = _axis(xs, margin, grid_size), _axis(ys, margin, grid_size)
    X, Y = np.meshgrid(gx, gy)
    Z = np.vectorize(f, otypes=[float])(X, Y)

    surface = go.Surface(x=gx, y=gy, z=Z, colorscale="Viridis", opacity=0.55,
                         showscale=False, name="f(x, y)", hoverinfo="skip")
    hover = "x=%{x:.4f}<br>y=%{y:.4f}<br>f=%{z:.4f}<extra></extra>"

    def path_trace(k):
        return go.Scatter3d(x=xs[:k + 1], y=ys[:k + 1], z=zs[:k + 1], mode="lines+markers",
                            line=dict(color="black", width=5), marker=dict(size=3, color="black"),
                            name="trajectory", hovertemplate=hover)

    def end_trace(k):
        return go.Scatter3d(x=[xs[k]], y=[ys[k]], z=[zs[k]], mode="markers+text",
                            marker=dict(size=9, color="red"),
                            text=[f"f = {zs[k]:.4g}"], textposition="top center",
                            name="end", hovertemplate=hover)

    start = go.Scatter3d(x=[xs[0]], y=[ys[0]], z=[zs[0]], mode="markers",
                         marker=dict(size=9, color="blue"), name="start", hovertemplate=hover)

    k0 = 0 if animate else n - 1
    fig = go.Figure(data=[surface, path_trace(k0), start, end_trace(k0)])
    if animate:
        _add_animation(fig, path_trace, end_trace, n, [1, 3], max_frames)

    fig.update_layout(scene=dict(xaxis_title="x", yaxis_title="y", zaxis_title="f(x, y)"),
                      margin=dict(l=0, r=0, t=30, b=0), legend=dict(x=0, y=1))
    if show:
        fig.show()
    return fig


def plot_path_contour(f, points, animate=False, margin=0.3, grid_size=100, show=True, max_frames=200):
    pts = _as_points(points, 2)
    xs, ys = pts[:, 0], pts[:, 1]
    fs = np.array([f(x, y) for x, y in pts], dtype=float)
    n = len(pts)

    gx, gy = _axis(xs, margin, grid_size), _axis(ys, margin, grid_size)
    X, Y = np.meshgrid(gx, gy)
    Z = np.vectorize(f, otypes=[float])(X, Y)

    contour = go.Contour(x=gx, y=gy, z=Z, colorscale="Viridis", opacity=0.6, showscale=False,
                         contours=dict(showlabels=True), name="f(x, y)", hoverinfo="skip")
    hover = "x=%{x:.4f}<br>y=%{y:.4f}<br>f=%{customdata:.4f}<extra></extra>"

    def path_trace(k):
        return go.Scatter(x=xs[:k + 1], y=ys[:k + 1], customdata=fs[:k + 1], mode="lines+markers",
                          line=dict(color="black", width=2), marker=dict(size=5, color="black"),
                          name="trajectory", hovertemplate=hover)

    def end_trace(k):
        return go.Scatter(x=[xs[k]], y=[ys[k]], customdata=[fs[k]], mode="markers+text",
                          marker=dict(size=14, color="red"),
                          text=[f"f = {fs[k]:.4g}"], textposition="top center",
                          name="end", hovertemplate=hover)

    start = go.Scatter(x=[xs[0]], y=[ys[0]], customdata=[fs[0]], mode="markers",
                       marker=dict(size=14, color="blue"), name="start", hovertemplate=hover)

    k0 = 0 if animate else n - 1
    fig = go.Figure(data=[contour, path_trace(k0), start, end_trace(k0)])
    if animate:
        _add_animation(fig, path_trace, end_trace, n, [1, 3], max_frames)

    fig.update_layout(xaxis_title="x", yaxis=dict(title="y", scaleanchor="x"),
                      margin=dict(l=40, r=20, t=30, b=40), legend=dict(x=1.02, y=1))
    if show:
        fig.show()
    return fig


def visualize_path(f, path, print_items=None, animate=True, contour=False):
    pts = _as_points(path)
    dim = pts.shape[1]

    if dim == 1:
        fig = plot_path_1d(f, pts, animate=animate, show=False)
    elif dim == 2:
        if contour:
            fig = plot_path_contour(f, pts, animate=animate, show=False)
        else:
            fig = plot_path_2d(f, pts, animate=animate, show=False)
    else:
        for item in (path if print_items is None else print_items):
            print(item)
        return None

    fig.write_html(
        "visualizations/optimization.html",
        include_plotlyjs=True
    )

    fig.show()
    return fig