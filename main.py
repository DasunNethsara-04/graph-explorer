import math
import numpy as np
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def safe_eval_expression(expr: str, x_array: np.ndarray) -> np.ndarray:
    """
    Safely evaluate an expression in x using a restricted namespace.
    Supported: +, -, *, /, **, parentheses, and common NumPy functions.
    Users can write e.g.: sin(x) + 0.5*x**2 or exp(-x)*sin(2*x)
    """
    # Normalize caret to Python power
    expr = expr.replace("^", "**")

    allowed = {
        # Variables
        "x": x_array,

        # Constants
        "pi": np.pi, "e": np.e,

        # Elementary
        "sin": np.sin, "cos": np.cos, "tan": np.tan,
        "asin": np.arcsin, "acos": np.arccos, "atan": np.arctan,
        "sinh": np.sinh, "cosh": np.cosh, "tanh": np.tanh,
        "exp": np.exp, "log": np.log, "log10": np.log10,
        "sqrt": np.sqrt, "abs": np.abs,
        "floor": np.floor, "ceil": np.ceil,
        "pow": np.power, "arctan2": np.arctan2,
        # Optional numpy exposure (limited)
        "np": np,
    }
    try:
        y = eval(expr, {"__builtins__": {}}, allowed)
        y = np.asarray(y, dtype=float)
    except Exception as ex:
        raise ValueError(f"Invalid expression: {ex}")
    return y


def slope_at_point(x: np.ndarray, y: np.ndarray, x0: float, window: int = 3) -> float:
    """
    Estimate slope (dy/dx) at x0 by fitting a local straight line (least squares).
    Picks points in a window around the nearest x to x0. Falls back gracefully.
    """
    if len(x) < 2:
        return float("nan")

    # Sort by x to compute neighbor windows robustly
    order = np.argsort(x)
    xs = x[order]
    ys = y[order]

    # Index of nearest x to x0
    idx = int(np.argmin(np.abs(xs - x0)))

    lo = max(0, idx - window)
    hi = min(len(xs), idx + window + 1)
    xw = xs[lo:hi]
    yw = ys[lo:hi]

    # If still insufficient unique x values, widen or fallback to global
    if len(np.unique(xw)) < 2:
        if len(np.unique(xs)) >= 2:
            # Use more points if possible
            xw = xs
            yw = ys
        else:
            return float("nan")

    try:
        # Linear fit: y ≈ m x + b
        m, b = np.polyfit(xw, yw, 1)
        return float(m)
    except Exception:
        return float("nan")


class XYTable(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.rows = []
        self._build_header()

    def _build_header(self):
        ctk.CTkLabel(self, text="x", width=80, anchor="w").grid(row=0, column=0, padx=6, pady=6, sticky="w")
        ctk.CTkLabel(self, text="y", width=80, anchor="w").grid(row=0, column=1, padx=6, pady=6, sticky="w")

    def add_row(self, x_val: str = "", y_val: str = ""):
        r = len(self.rows) + 1
        ex = ctk.CTkEntry(self, width=120)
        ey = ctk.CTkEntry(self, width=120)
        ex.insert(0, str(x_val))
        ey.insert(0, str(y_val))
        ex.grid(row=r, column=0, padx=6, pady=4, sticky="w")
        ey.grid(row=r, column=1, padx=6, pady=4, sticky="w")
        self.rows.append((ex, ey))

    def clear(self):
        for ex, ey in self.rows:
            ex.destroy()
            ey.destroy()
        self.rows.clear()

    def get_data(self):
        xs, ys = [], []
        for ex, ey in self.rows:
            sx = ex.get().strip()
            sy = ey.get().strip()
            if sx == "" and sy == "":
                continue
            if sx == "" or sy == "":
                raise ValueError("Each row must have both x and y values.")
            try:
                xv = float(sx)
                yv = float(sy)
            except ValueError:
                raise ValueError(f"Invalid number: x='{sx}', y='{sy}'")
            xs.append(xv)
            ys.append(yv)
        if len(xs) == 0:
            raise ValueError("Please enter at least one (x, y) pair.")
        return np.array(xs, dtype=float), np.array(ys, dtype=float)


class GraphApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Graph Explorer")
        self.geometry("1100x680")
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")

        self.mode = tk.StringVar(value="Using x, y values")
        self._build_layout()
        self._build_plot()
        self._show_mode(self.mode.get())

    def _build_layout(self):
        self.grid_columnconfigure(0, weight=0, minsize=380)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Left panel
        self.left = ctk.CTkFrame(self, corner_radius=0)
        self.left.grid(row=0, column=0, sticky="nsew")
        self.left.grid_rowconfigure(3, weight=1)

        title = ctk.CTkLabel(self.left, text="Graph Explorer", font=ctk.CTkFont(size=18, weight="bold"))
        title.grid(row=0, column=0, padx=16, pady=(16, 8), sticky="w")

        self.segment = ctk.CTkSegmentedButton(
            self.left,
            values=["Using x, y values", "Using Equation"],
            variable=self.mode,
            command=self._on_mode_change
        )
        self.segment.grid(row=1, column=0, padx=16, pady=(0, 12), sticky="ew")

        self.stack = ctk.CTkFrame(self.left)
        self.stack.grid(row=2, column=0, padx=12, pady=8, sticky="nsew")
        self.stack.grid_columnconfigure(0, weight=1)

        # XY panel
        self.xy_panel = ctk.CTkFrame(self.stack)
        self.xy_panel.grid_columnconfigure(0, weight=1)

        xy_hint = ctk.CTkLabel(self.xy_panel, text="Enter data points below. Add rows as needed.")
        xy_hint.grid(row=0, column=0, padx=8, pady=(8, 4), sticky="w")

        self.xy_table = XYTable(self.xy_panel, width=340, height=260)
        self.xy_table.grid(row=1, column=0, padx=8, pady=8, sticky="nsew")

        btns = ctk.CTkFrame(self.xy_panel)
        btns.grid(row=2, column=0, padx=8, pady=(0, 8), sticky="ew")
        btns.grid_columnconfigure((0, 1, 2), weight=1)

        add_btn = ctk.CTkButton(btns, text="Add row", command=lambda: self.xy_table.add_row("", ""))
        add_btn.grid(row=0, column=0, padx=6, pady=6, sticky="ew")

        clear_btn = ctk.CTkButton(btns, text="Clear", command=self.xy_table.clear)
        clear_btn.grid(row=0, column=1, padx=6, pady=6, sticky="ew")

        sample_btn = ctk.CTkButton(btns, text="Load sample", command=self._load_xy_sample)
        sample_btn.grid(row=0, column=2, padx=6, pady=6, sticky="ew")

        # Equation panel
        self.eq_panel = ctk.CTkFrame(self.stack)
        self.eq_panel.grid_columnconfigure(1, weight=1)

        eq_label = ctk.CTkLabel(self.eq_panel, text="Enter equation for y in terms of x:")
        eq_label.grid(row=0, column=0, columnspan=2, padx=8, pady=(8, 4), sticky="w")

        ctk.CTkLabel(self.eq_panel, text="y =").grid(row=1, column=0, padx=(8, 4), pady=4, sticky="w")
        self.eq_entry = ctk.CTkEntry(self.eq_panel, placeholder_text="e.g., sin(x) + 0.5*x**2")
        self.eq_entry.grid(row=1, column=1, padx=(0, 8), pady=4, sticky="ew")
        self.eq_entry.insert(0, "sin(x) + 0.5*x")

        range_frame = ctk.CTkFrame(self.eq_panel)
        range_frame.grid(row=2, column=0, columnspan=2, padx=8, pady=6, sticky="ew")
        range_frame.grid_columnconfigure((1, 3, 5), weight=1)

        ctk.CTkLabel(range_frame, text="x min").grid(row=0, column=0, padx=4, pady=4, sticky="w")
        self.xmin_entry = ctk.CTkEntry(range_frame)
        self.xmin_entry.grid(row=0, column=1, padx=4, pady=4, sticky="ew")
        self.xmin_entry.insert(0, "-10")

        ctk.CTkLabel(range_frame, text="x max").grid(row=0, column=2, padx=4, pady=4, sticky="w")
        self.xmax_entry = ctk.CTkEntry(range_frame)
        self.xmax_entry.grid(row=0, column=3, padx=4, pady=4, sticky="ew")
        self.xmax_entry.insert(0, "10")

        ctk.CTkLabel(range_frame, text="points").grid(row=0, column=4, padx=4, pady=4, sticky="w")
        self.npts_entry = ctk.CTkEntry(range_frame)
        self.npts_entry.grid(row=0, column=5, padx=4, pady=4, sticky="ew")
        self.npts_entry.insert(0, "400")

        # Draw button + status
        draw = ctk.CTkButton(self.left, text="Draw the Chart", command=self.draw_chart)
        draw.grid(row=3, column=0, padx=16, pady=8, sticky="ew")

        self.status = ctk.CTkLabel(self.left, text="G Point: —    |    Slope at G: —")
        self.status.grid(row=4, column=0, padx=16, pady=(4, 16), sticky="w")

        # Right panel (plot)
        self.right = ctk.CTkFrame(self, corner_radius=0)
        self.right.grid(row=0, column=1, sticky="nsew")
        self.right.grid_rowconfigure(0, weight=1)
        self.right.grid_columnconfigure(0, weight=1)

    def _build_plot(self):
        self.fig = Figure(figsize=(6, 5), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Your chart will appear here")
        self.ax.set_xlabel("x")
        self.ax.set_ylabel("y")
        self.ax.grid(True, alpha=0.3)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.right)
        self.canvas.get_tk_widget().grid(row=0, column=0, padx=8, pady=8, sticky="nsew")
        self.canvas.draw()

    def _on_mode_change(self, mode_value: str):
        self._show_mode(mode_value)

    def _show_mode(self, mode_value: str):
        for w in (self.xy_panel, self.eq_panel):
            w.grid_forget()
        if mode_value == "Using x, y values":
            self.xy_panel.grid(row=0, column=0, padx=8, pady=8, sticky="nsew")
        else:
            self.eq_panel.grid(row=0, column=0, padx=8, pady=8, sticky="nsew")

    def _load_xy_sample(self):
        self.xy_table.clear()
        # Sample: y = x^2 for x in [-2,-1,0,1,2]
        for xv in [-2, -1, 0, 1, 2]:
            self.xy_table.add_row(str(xv), str(xv * xv))
        # Add a blank row for convenience
        self.xy_table.add_row("", "")

    def _plot_points(self, x, y, title_info=""):
        self.ax.clear()
        self.ax.grid(True, alpha=0.3)
        self.ax.set_xlabel("x")
        self.ax.set_ylabel("y")

        mask = np.isfinite(x) & np.isfinite(y)
        x = x[mask]
        y = y[mask]

        if len(x) == 0:
            raise ValueError("No valid finite data to plot.")

        # Scatter the raw points
        self.ax.scatter(x, y, color="#1f77b4", s=50, label="Data points")

        # If using x,y values, draw best fit line
        if self.mode.get() == "Using x, y values" and len(x) >= 2:
            coeffs = np.polyfit(x, y, deg=1)  # Linear regression
            y_fit = np.polyval(coeffs, x)
            order = np.argsort(x)
            self.ax.plot(x[order], y_fit[order], color="#ff7f0e", linewidth=2, label="Best fit line")
            slope_fit = coeffs[0]
        else:
            slope_fit = None

        # G Point
        Gx = float(np.mean(x))
        Gy = float(np.mean(y))
        self.ax.scatter([Gx], [Gy], color="#d62728", marker="X", s=90, label="G Point")

        # Random points
        rng = np.random.default_rng()
        if len(x) >= 2:
            rand_idx = rng.choice(len(x), size=min(2, len(x)), replace=False)
            rx, ry = x[rand_idx], y[rand_idx]
            self.ax.scatter(rx, ry, color="#2ca02c", s=60, label="Random points")
            for xi, yi in zip(rx, ry):
                self.ax.annotate(f"({xi:.3g}, {yi:.3g})", (xi, yi),
                                 textcoords="offset points", xytext=(8, 6), fontsize=8)

        # Slope at G
        if slope_fit is not None:
            mG = slope_fit
        else:
            mG = slope_at_point(x, y, Gx, window=3)

        subtitle = f"G=({Gx:.4g}, {Gy:.4g})   |   slope at G={mG:.4g}" if not math.isnan(
            mG) else f"G=({Gx:.4g}, {Gy:.4g})"
        self.ax.set_title(title_info + ("\n" if title_info else "") + subtitle)
        self.ax.legend(loc="best", fontsize=9)

        slope_text = f"{mG:.6g}" if not math.isnan(mG) else "—"
        self.status.configure(text=f"G Point: ({Gx:.6g}, {Gy:.6g})    |    Slope at G: {slope_text}")

        self.canvas.draw()

    def draw_chart(self):
        try:
            if self.mode.get() == "Using x, y values":
                x, y = self.xy_table.get_data()
                if len(x) < 2:
                    raise ValueError("Please enter at least two points to draw a chart.")
                # Sort by x for a sensible path
                order = np.argsort(x)
                x = x[order]
                y = y[order]
                self._plot_points(x, y, title_info="From x, y values")
            else:
                expr = self.eq_entry.get().strip()
                if expr == "":
                    raise ValueError("Please enter an equation for y in terms of x.")
                try:
                    xmin = float(self.xmin_entry.get().strip())
                    xmax = float(self.xmax_entry.get().strip())
                    npts = int(float(self.npts_entry.get().strip()))
                except ValueError:
                    raise ValueError("x-range and points must be numeric.")

                if not (xmax > xmin):
                    raise ValueError("x max must be greater than x min.")
                if npts < 10:
                    raise ValueError("Use at least 10 points for a meaningful curve.")

                x = np.linspace(xmin, xmax, npts)
                y = safe_eval_expression(expr, x)
                if y.shape != x.shape:
                    raise ValueError("The expression did not evaluate to a vector of y values.")
                self._plot_points(x, y, title_info=f"y = {expr}")
        except Exception as ex:
            messagebox.showerror("Error", str(ex))


if __name__ == "__main__":
    app = GraphApp()

    for _ in range(5):
        app.xy_table.add_row("", "")
    app.mainloop()