import matplotlib.pyplot as plt
import pandas as pd

def plot_graph_labeled_results_PM_temp(csv_path):
    """
    Plot graph from labeled CSV results.

    Args:
        csv_path (str): Path to the labeled CSV file.
    """
    df = pd.read_csv(csv_path)

    df["Date"] = df["Date"] + " " + df["Time"]

    #group labels
    unique_label = df['Auto_Label'].unique()  # Replace
    print(unique_label)

    count_label = {}
    for label in unique_label:
        count_label[label] = (df['Auto_Label'] == label).sum()

    # --- ส่วนการพล็อตกราฟ ---
    plt.rcParams.update({'font.family': 'tahoma'})
    fig, axs = plt.subplots(2,1,figsize=(12, 6))

    # Plot PM2.5 (แกนซ้าย - สีแดง)

    ax1 = axs[0]
    ax1.set_title('PM2.5 vs Temperature (Nov 30 - Dec 2, 2025 - Bangkok)')
    color = 'tab:red'
    ax1.set_xlabel('Time (Hours)')
    ax1.set_ylabel('PM2.5 (µg/m³)', color=color)
    ax1.plot(df['Date'], df['PM2.5'], color=color,marker='o', linestyle='-', label='PM2.5')
    ax1.set_xticks(ax1.get_xticks(), ax1.get_xticklabels(), rotation=60, ha='right')
    ax1.tick_params(axis='y', labelcolor=color)

    # Plot Temperature (แกนขวา - สีน้ำเงิน)
    ax2 = ax1.twinx()  
    color = 'tab:blue'
    ax2.set_ylabel('Temperature (°C)', color=color)
    ax2.plot(df['Date'], df['Temp'], color=color,marker='o', linestyle='-', label='Temp')
    ax2.tick_params(axis='y', labelcolor=color)

    # Plot areas for each label that next each other
    prev_label = ""
    start_index = 0
    end_index = 0
    for item in df.iterrows():
        index, row = item
        label = row['Auto_Label']

        if label != prev_label or index == len(df) - 1:
            if index == len(df) - 1:
                end_index = index
            else:
                end_index = index - 1
            if prev_label != "":
                color = 'tab:red' if prev_label.find("risk") != -1 else 'tab:orange' if prev_label.find("Hot") != -1 else 'w'
                ax1.axvspan(df['Date'][start_index], df['Date'][end_index], alpha=0.3,color = color, label=prev_label)
            start_index = index
            prev_label = label

    ax2 = axs[1]
    ax2.set_title('Count of Auto-Labels')
    ax2.set_xlabel('Auto-Label')
    ax2.set_ylabel('Count')
    # plot count label bar chart
    bar_colors = ['tab:green' if label == 'Normal' else 'tab:red' if label.find("risk") != -1 else 'tab:orange' for label in count_label.keys()]
    ax2.bar(count_label.keys(), count_label.values(),color=bar_colors,alpha=0.3)

    # plt.title('PM2.5 vs Temperature (Nov 30 - Dec 2, 2025 - Bangkok)')
    fig.tight_layout()
    plt.show()

if __name__ == "__main__":
    csv_path = "data/PM_Temp_labeled.csv"  # Example path
    plot_graph_labeled_results_PM_temp(csv_path)