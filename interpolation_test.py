import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d , CubicSpline
import numpy as np
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image ,Spacer
from reportlab.lib.styles import getSampleStyleSheet

signal1 = pd.read_csv('data_1.csv')
signal2 = pd.read_csv('data_2.csv')

data1 = signal1['MLII']
data2 = signal2['MLII']

data1_x = data1.index.to_list()
data1_y = data1.values

data2_x = data2.index.to_list()
data2_x = [x + 2000 for x in data2_x]
data2_y = data2.values

if (data1_x[-1] > data2_x[0] ):
    overlap_start = max(min(data2_x) ,min(data1_x))
    overlap_end = min(max(data2_x) ,max(data1_x))
    
    interpolation_function_data_1 = interp1d(data1_x , data1_y ,kind='quadratic')
    interpolation_function_data_2 = interp1d(data2_x , data2_y ,kind='quadratic')

    x_overlapped = np.linspace(overlap_start , overlap_end , num = 1000)
    
    data_1_interpolated = interpolation_function_data_1(x_overlapped)
    data_2_interpolated = interpolation_function_data_2(x_overlapped)
    
    y_interpolated = (data_1_interpolated + data_2_interpolated) / 2
    plt.plot(data1)
    plt.plot(data2)
    plt.plot(x_overlapped, y_interpolated , linestyle ='--')
else:
    x_gap = np.linspace(data1_x[-1] , data2_x[0], num = 1000)
    data_x = np.concatenate([data1_x, data2_x])
    data_y = np.concatenate([data1_y, data2_y])
    interpolation_function_data_1 = interp1d(data_x , data_y ,kind='quadratic' ,fill_value="extrapolate")
    # data_1_interpolated = interpolation_function_data_1(x_gap)
    # y_interpolated = data_1_interpolated
    
    # interpolation_function_data_1 = interp1d(data1_x , data1_y ,kind='quadratic' ,fill_value='extrapolate')
    # interpolation_function_data_2 = interp1d(data2_x , data2_y ,kind='quadratic', fill_value='extrapolate')
    # data_1_interpolated = interpolation_function_data_1(x_gap)
    # data_2_interpolated = interpolation_function_data_2(x_gap)
    # y_interpolated = (data_1_interpolated + data_2_interpolated) / 2
    
    
    
    # plt.plot(x_gap, y_interpolated , linestyle ='--')
    
    # cs = CubicSpline(data_x, data_y)
    # gap_y = cs(x_gap)
    gap_y = interpolation_function_data_1(x_gap)
    print(gap_y)
    plt.plot(x_gap , gap_y)
        
plt.plot(data1_x , data1_y)
plt.plot(data2_x , data2_y)
glued_signal_x = np.concatenate([data1_x , x_gap , data2_x])
glued_signal_y = np.concatenate([data1_y, gap_y , data2_y])
glued_signal = np.column_stack((glued_signal_x, glued_signal_y))
# plt.savefig("youssef.png")
plt.show()
# print(glued_signal)
statistics = {
    "mean" : np.mean(glued_signal_y),
    "std"  : np.std(glued_signal_y),
    "min"  : np.min(glued_signal_y),
    "max"  : np.max(glued_signal_y),
    "duration" : len(glued_signal_x)
}
def create_pdf_report():
    pdf_file = 'report.pdf'
    document = SimpleDocTemplate(pdf_file , pagesize= letter)
    styles = getSampleStyleSheet()
    story = []
    
    story.append(Paragraph("Report for Youssef" , styles['Title']))
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
    combined_table = Table(combined_data, colWidths=[4 * inch, 2 * inch])  # Adjust column widths as needed
    
    # Add the combined table to the story
    story.append(combined_table)
    story.append(Spacer(1, 12))  # Add space between sections

    document.build(story)

# create_pdf_report()
    