import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import numpy as np
from filterpy.kalman import KalmanFilter
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from scipy.interpolate import CubicSpline

# Read signals
signal1 = pd.read_csv('data_1.csv')
signal2 = pd.read_csv('data_2.csv')

data1 = signal1['MLII']
data2 = signal2['MLII']

data1_x = data1.index.to_list()
data1_y = data1.values

data2_x = data2.index.to_list()
data2_x = [x + 2000 for x in data2_x]  # Adjust the x-axis of data2 to match

data2_y = data2.values


def cubic_spline_interpolation(data1_x, data1_y, data2_x, data2_y, gap_x):
    combined_x = np.concatenate([data1_x, data2_x])
    combined_y = np.concatenate([data1_y, data2_y])
    
    # Create cubic spline interpolation
    cs = CubicSpline(combined_x, combined_y)
    return cs(gap_x)

# Kalman Filter interpolation for gap
def kalman_filter_interpolation(x1, y1, x2, y2, gap_x):
    # Initialize Kalman Filter
    kf = KalmanFilter(dim_x=2, dim_z=1)  # State vector [position, velocity]
    dt = 1.0  # Assuming constant time step

    # State transition matrix with damping
    kf.F = np.array([[1, dt], [0, 0.9]])  # 0.9 factor for damping velocity to reduce overshooting

    # Measurement function: we only measure position
    kf.H = np.array([[1, 0]])  

    # Covariance matrices
    kf.P *= 5.0  # Initial uncertainty
    kf.R = 0.5  # Measurement noise
    kf.Q = np.array([[0.01, 0], [0, 0.01]])  # Process noise

    # Estimate the initial state based on the trend at the end of signal 1
    initial_velocity = (y1[-1] - y1[-2]) / (x1[-1] - x1[-2])
    kf.x = np.array([[y1[-1]], [initial_velocity]])  # Initial state [position, velocity]

    interpolated_gap_y = []

    # Kalman filter prediction loop for the gap
    for x in gap_x:
        kf.predict()  # Predict the next position and velocity
        interpolated_gap_y.append(kf.x[0][0])  # Store only the position estimate

    return np.array(interpolated_gap_y)  # Return interpolated positions


# If there's an overlap
if (data1_x[-1] > data2_x[0]):
    # Handle overlap using interpolation
    overlap_start = max(min(data2_x), min(data1_x))
    overlap_end = min(max(data2_x), max(data1_x))

    interpolation_function_data_1 = interp1d(data1_x, data1_y, kind='quadratic')
    interpolation_function_data_2 = interp1d(data2_x, data2_y, kind='quadratic')

    x_overlapped = np.linspace(overlap_start, overlap_end, num=1000)
    data_1_interpolated = interpolation_function_data_1(x_overlapped)
    data_2_interpolated = interpolation_function_data_2(x_overlapped)
    y_interpolated = (data_1_interpolated + data_2_interpolated) / 2
    
    # plt.plot(x_overlapped, y_interpolated, linestyle='--')

else:
    # Handle the gap using the Kalman filter
    gap_x = np.linspace(data1_x[-1], data2_x[0], num=1000)
    gap_y = kalman_filter_interpolation(data1_x, data1_y, data2_x, data2_y, gap_x)
    
    # plt.plot(gap_x, gap_y, linestyle='--')

gap_y_spline = cubic_spline_interpolation(data1_x, data1_y, data2_x, data2_y, gap_x)
gap_y_kalman = kalman_filter_interpolation(data1_x, data1_y, data2_x, data2_y, gap_x)

# Combine both interpolations for smoother result
gap_y_combined = (gap_y_spline + gap_y_kalman) / 2
plt.plot(gap_x, gap_y_combined, linestyle='--', color='purple', label='Kalman & Spline Blend')

# Plot the original data
plt.plot(data1_x, data1_y, label='Signal 1')
plt.plot(data2_x, data2_y, label='Signal 2')

# Combine the signals
glued_signal_x = np.concatenate([data1_x, gap_x, data2_x])
glued_signal_y = np.concatenate([data1_y, gap_y, data2_y])
glued_signal = np.column_stack((glued_signal_x, glued_signal_y))

plt.plot(glued_signal_x, glued_signal_y, label='Combined Signal')
plt.legend()
plt.show()

# Statistics for report
statistics = {
    "mean": np.mean(glued_signal_y),
    "std": np.std(glued_signal_y),
    "min": np.min(glued_signal_y),
    "max": np.max(glued_signal_y),
    "duration": len(glued_signal_x)
}

# Create PDF Report
def create_pdf_report():
    pdf_file = 'report.pdf'
    document = SimpleDocTemplate(pdf_file, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("Report for Youssef", styles['Title']))
    img_path = "youssef.png"
    image = Image(img_path, width=4 * inch, height=3 * inch)

    data = [
        ['Statistic', 'Value'],
        ['Mean', f"{statistics['mean']:.2f}"],
        ['Standard Deviation', f"{statistics['std']:.2f}"],
        ['Duration', str(statistics['duration'])],
        ['Min', f"{statistics['min']:.2f}"],
        ['Max', f"{statistics['max']:.2f}"]
    ]

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    combined_data = [[image, table]]
    combined_table = Table(combined_data, colWidths=[4 * inch, 2 * inch])

    story.append(combined_table)
    story.append(Spacer(1, 12))

    document.build(story)

# create_pdf_report()
