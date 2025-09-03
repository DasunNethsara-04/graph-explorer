# 📊 Graph Explorer

**Graph Explorer** is a Python desktop application built with [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) and [Matplotlib](https://matplotlib.org/) that lets you **visualize mathematical or physics graphs** in two ways:

1. **Using x, y values** — Enter your own data points in a dynamic table.
2. **Using an equation** — Type a mathematical expression for `y` in terms of `x`.

It automatically calculates and displays:
- The **G Point** (centroid) of the plotted data.
- At least **two random points** from the curve.
- The **slope/gradient** at the G Point.
- The **best fit line** (when plotting from x, y values) to show the trend.

---

## ✨ Features

- **Two plotting modes**:
  - **Using x, y values**: Enter data in a scrollable, dynamic table.
  - **Using Equation**: Input an equation like `sin(x) + 0.5*x**2` with custom x‑range and resolution.
- **Best Fit Line**: Automatically fits and overlays a regression line when plotting from data points.
- **G Point Calculation**: Shows the centroid `(mean(x), mean(y))` on the chart.
- **Random Points Highlighting**: Marks two random points from the dataset with coordinates.
- **Slope at G Point**: Calculates the gradient at the centroid.
- **User-Friendly UI**:
  - Modern look with **CustomTkinter**.
  - Clear layout and responsive design.
  - Sample data loader for quick testing.

---

## 🖥️ Screenshots

<img width="1920" height="1080" alt="Screenshot (9)" src="https://github.com/user-attachments/assets/fe0a3aa2-782f-4255-9a8f-acce151ba350" />
<img width="1920" height="1080" alt="Screenshot (13)" src="https://github.com/user-attachments/assets/e48911c5-208d-456e-bcd5-61a217bcc6d2" />
<img width="1920" height="1080" alt="Screenshot (12)" src="https://github.com/user-attachments/assets/14e22651-ac46-4aeb-b707-8c3a5ec3ae65" />
<img width="1920" height="1080" alt="Screenshot (11)" src="https://github.com/user-attachments/assets/52632715-fccc-417d-b8b6-f29423304ca1" />
<img width="1920" height="1080" alt="Screenshot (10)" src="https://github.com/user-attachments/assets/c5ad4483-3731-43f7-bd16-c651727b4ac8" />



---

## ⚙️ Installation & Setup

### 1️⃣ Clone the repository
```bash
git clone https://github.com/<your-username>/graph-explorer.git
cd graph-explorer
```

### 2️⃣ Install dependencies
Make sure you have Python 3.9+ installed.
```bash
pip install customtkinter matplotlib numpy
```

### 3️⃣ Run the application
```bash
python main.py
```

## 📌 Usage
### Mode 1: Using x, y values
- Select "Using x, y values" from the toggle.
- Enter your data points in the table.
- Click "Add row" to add more points.
- Click "Draw the Chart" to plot:
- Blue dots = your data points.
- Orange line = best fit line.
- Red X = G Point.
- Green dots = random points.
### Mode 2: Using Equation
- Select "Using Equation" from the toggle.
- Enter your equation for y in terms of x (e.g., sin(x) + 0.5*x).
- Set x min, x max, and points (resolution).
- Click "Draw the Chart" to plot:
- Blue curve = equation output.
- Red X = G Point.
- Green dots = random points.

## 📐 Example Equations
- sin(x) + 0.5*x
- cos(2*x)
- exp(-0.2*x)*sin(3*x)
- sqrt(abs(x))


## 📄 License
This project is licensed under the MIT License — see the LICENSE file for details.

## 🙌 Acknowledgements
- CustomTkinter for the modern Tkinter UI.
- Matplotlib for plotting.
- NumPy for numerical calculations.

## 🚀 Future Enhancements
- Option to choose polynomial degree for best fit.
- Export chart as PNG/JPEG.
- Display R² value for regression fit.
- CSV import/export for x, y data.
