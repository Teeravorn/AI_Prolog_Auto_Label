import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.colors import to_rgb
#POC MOCKUP

def _is_dark_color(color):
    try:
        r, g, b = to_rgb(color)
        luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b
        return luminance < 0.5
    except Exception:
        return False

def plot_labeled_results(csv_path):
    """
    Plot visualization of labeled data.
    
    Args:
        csv_path (str): Path to the labeled CSV file
    """
    try:
        df = pd.read_csv(csv_path)
        
        df["Date"] = df["Date"] + " " + df["Time"]

        # Create figure with subplots
        plt.rcParams.update({'font.family': 'tahoma'})
        fig, axes = plt.subplots(2, 1, figsize=(12, 10))
        
        # Plot 1: PM2.5 and Temperature over time with label areas
        ax1 = axes[0]
        # ax1.plot(df.index, df['PM2.5'], label='PM2.5', color='red', alpha=0.7, linewidth=2, zorder=3)
        ax1.plot(df["Date"], df['PM2.5'], label='PM2.5', color='red', alpha=0.7, linewidth=2, zorder=3)
        ax1.set_ylabel('PM2.5 (μg/m³)', color='red', fontsize=12)
        ax1.tick_params(axis='y', labelcolor='red')
        # ax1.set_xlabel('Row Index', fontsize=12)
        ax1.set_xlabel('DateTime', fontsize=12)
        ax1.set_xticks(ax1.get_xticks(), ax1.get_xticklabels(), rotation=60, ha='right')
        ax1.legend(loc='upper left', fontsize=10)
        ax1.grid(True, alpha=0.3)
        
        ax1_twin = ax1.twinx()
        # ax1_twin.plot(df.index, df['Temp'], label='Temperature', color='blue', alpha=0.7, linewidth=2, zorder=3)
        ax1_twin.plot(df["Date"], df['Temp'], label='Temperature', color='blue', alpha=0.7, linewidth=2, zorder=3)
        ax1_twin.set_ylabel('Temperature (°C)', color='blue', fontsize=12)
        ax1_twin.tick_params(axis='y', labelcolor='blue')
        ax1_twin.legend(loc='upper right', fontsize=10)
        
        # Find continuous labeled regions
        labeled_rows = df[df['auto_label'].notna() & (df['auto_label'] != '')]
        
        # Get unique labels and assign colors using Set3 (same palette as bar chart)
        unique_labels = labeled_rows['auto_label'].unique()
        label_colors = plt.cm.Set3(range(max(1, len(unique_labels))))
        label_color_map = dict(zip(unique_labels, label_colors))
        
        # Group consecutive indices with same label
        if len(labeled_rows) > 0:
            regions = []
            current_label = None
            start_idx = None
            
            for idx, row in df.iterrows():
                label = row['auto_label']
                
                # Skip empty labels
                if pd.isna(label) or label == '':
                    if current_label is not None:
                        # End of region
                        regions.append({
                            'label': current_label,
                            'start': start_idx,
                            'end': idx - 1
                        })
                        current_label = None
                    continue
                
                # Start new region or continue current
                if label != current_label:
                    if current_label is not None:
                        # End previous region
                        regions.append({
                            'label': current_label,
                            'start': start_idx,
                            'end': idx - 1
                        })
                    # Start new region
                    current_label = label
                    start_idx = idx
            
            # Close last region if exists
            if current_label is not None:
                regions.append({
                    'label': current_label,
                    'start': start_idx,
                    'end': df.index[-1]
                })
            
            # Draw shaded areas for each region
            for region in regions:
                label_text = region['label']
                start = region['start']
                end = region['end']
                color = label_color_map.get(label_text, 'gray')
                
                # Shade area
                ax1.axvspan(start, end, alpha=0.2, color=color, zorder=1)
                
                # Add text label at middle of region
                mid_idx = (start + end) // 2
                if mid_idx in df.index:
                    pm_value = df.loc[mid_idx, 'PM2.5']

                    # Add annotation at middle of region with readable contrast
                    text_color = 'white' if _is_dark_color(color) else 'black'
                    ax1.annotate(label_text,
                                 xy=(mid_idx, pm_value),
                                 xytext=(0, 30),
                                 textcoords='offset points',
                                 fontsize=9,
                                 color=text_color,
                                 bbox=dict(boxstyle='round,pad=0.5', fc=color, alpha=0.8,
                                           edgecolor='black', linewidth=1.5),
                                 ha='center',
                                 zorder=10)
        
        ax1.set_title('PM2.5 and Temperature Over Time with Labeled Regions', fontsize=14, fontweight='bold')
        
        # Plot 2: Label distribution
        ax2 = axes[1]
        label_counts = df['auto_label'].value_counts()
        # Remove empty labels
        label_counts = label_counts[label_counts.index != '']
        
        if len(label_counts) > 0:
            # Use the same colors as shaded regions so bars correspond to labels
            bar_colors = [label_color_map.get(l, 'gray') for l in label_counts.index]
            label_counts.plot(kind='bar', ax=ax2, color=bar_colors, edgecolor='black', linewidth=1.2)
            ax2.set_title('Label Distribution', fontsize=14, fontweight='bold')
            ax2.set_xlabel('Labels', fontsize=12)
            ax2.set_ylabel('Count', fontsize=12)
            ax2.tick_params(axis='x', rotation=0)
            ax2.grid(True, alpha=0.3, axis='y')
            
            # Add count labels on bars
            for i, v in enumerate(label_counts):
                ax2.text(i, v + 0.5, str(v), ha='center', va='bottom', fontweight='bold')
        else:
            ax2.text(0.5, 0.5, 'No labels applied', 
                    ha='center', va='center', fontsize=16, color='gray')
            ax2.set_title('Label Distribution', fontsize=14, fontweight='bold')
            ax2.set_xlim(0, 1)
            ax2.set_ylim(0, 1)
        
        plt.tight_layout()
        
        # Save plot
        plot_path = csv_path.replace('.csv', '_plot.png')
        plt.savefig(plot_path, dpi=100, bbox_inches='tight')
        print(f"Plot saved to: {plot_path}")
        
        # Show plot
        plt.show()
        
        return plot_path
        
    except Exception as e:
        print(f"Error plotting results: {e}")
        return None


if __name__ == "__main__":
    # Example usage
    import sys
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
        plot_labeled_results(csv_file)
    else:
        print("Usage: python render_graph.py <path_to_labeled_csv>")


def plot_rain_labeled_dataframe(df, save_path=None):
    """
    Plot labeled weather/rain forecast data from a DataFrame.

    Produces two subplots:
    - Temperature, Humidity, Pressure over time with shaded regions by `auto_label`.
    - Label distribution bar chart (counts per `auto_label`).

    Args:
        df (pd.DataFrame): DataFrame containing `Temp`, `Humidity`, `Pressure` and `auto_label`.
        save_path (str|None): If provided, saves the plot to this path.

    Returns:
        str|None: Saved path or None.
    """
    df_plot = df.copy().reset_index(drop=True)

    # Normalize column names
    if 'Temp' in df_plot.columns and 'Temperature' not in df_plot.columns:
        df_plot['Temperature'] = df_plot['Temp']

    # Create figure
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))
    ax1 = axes[0]

    # Plot Temperature on left axis
    ax1.plot(df_plot["Date"], df_plot['Temperature'], label='Temperature (°C)', color='orange', linewidth=2, zorder=3)
    # ax1.plot(df_plot.index, df_plot['Temperature'], label='Temperature (°C)', color='orange', linewidth=2, zorder=3)
    ax1.set_ylabel('Temperature (°C)', color='orange', fontsize=12)
    ax1.tick_params(axis='y', labelcolor='orange')
    ax1.set_xlabel('Day', fontsize=12)
    ax1.set_xticks(ax1.get_xticks(), ax1.get_xticklabels(), rotation=60, ha='right')
    ax1.grid(True, alpha=0.3)

    # Twin axis for Humidity
    ax1_twin = ax1.twinx()
    ax1_twin.plot(df_plot["Date"], df_plot['Humidity'], label='Humidity (%)', color='steelblue', linewidth=2, alpha=0.7, zorder=3)
    ax1_twin.plot(df_plot.index, df_plot['Humidity'], label='Humidity (%)', color='steelblue', linewidth=2, alpha=0.7, zorder=3)
    ax1_twin.set_ylabel('Humidity (%)', color='steelblue', fontsize=12)
    ax1_twin.tick_params(axis='y', labelcolor='steelblue')

    # Shade regions by auto_label (reuse label_color_map logic)
    if 'auto_label' in df_plot.columns:
        labels_series = df_plot['auto_label'].fillna('').astype(str)
    else:
        labels_series = pd.Series([''] * len(df_plot))

    unique_labels = [l for l in pd.unique(labels_series) if l != '']
    label_colors = plt.cm.Set3(range(max(1, len(unique_labels))))
    label_color_map = dict(zip(unique_labels, label_colors))

    regions = []
    current_label = None
    start_idx = None
    for i, lbl in enumerate(labels_series):
        if lbl == '' or pd.isna(lbl):
            if current_label is not None:
                regions.append({'label': current_label, 'start': start_idx, 'end': i - 1})
                current_label = None
            continue
        if lbl != current_label:
            if current_label is not None:
                regions.append({'label': current_label, 'start': start_idx, 'end': i - 1})
            current_label = lbl
            start_idx = i
    if current_label is not None:
        regions.append({'label': current_label, 'start': start_idx, 'end': len(df_plot) - 1})

    for region in regions:
        label_text = region['label']
        start = region['start']
        end = region['end']
        color = label_color_map.get(label_text, 'gray')
        span_start = max(0, start - 0.4)
        span_end = min(len(df_plot) - 1, end + 0.4)
        ax1.axvspan(span_start, span_end, alpha=0.25, facecolor=color, edgecolor='k', linewidth=0.6, zorder=1)

        mid_idx = (start + end) // 2
        if 0 <= mid_idx < len(df_plot):
            temp_value = df_plot.loc[mid_idx, 'Temperature']
            annotate_text = str(label_text)
            ax1.annotate(annotate_text,
                         xy=(mid_idx, temp_value),
                         xytext=(0, 20),
                         textcoords='offset points',
                         fontsize=9,
                         color='white' if _is_dark_color(color) else 'black',
                         bbox=dict(boxstyle='round,pad=0.5', fc=color, alpha=0.85,
                                   edgecolor='black', linewidth=1.0),
                         ha='center',
                         zorder=10)

    ax1.set_title('Weather Predictors Over Time with Rain Forecast Labels', fontsize=14, fontweight='bold')

    # Label distribution
    ax2 = axes[1]
    if 'auto_label' in df_plot.columns:
        label_counts = df_plot['auto_label'].fillna('').value_counts()
        label_counts = label_counts[label_counts.index != '']
    else:
        label_counts = pd.Series([], dtype=int)

    if len(label_counts) > 0:
        bar_colors = [label_color_map.get(l, 'gray') for l in label_counts.index]
        label_counts.plot(kind='bar', ax=ax2, color=bar_colors, edgecolor='black', linewidth=1.2)
        ax2.set_title('Forecast Label Distribution', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Labels', fontsize=12)
        ax2.set_ylabel('Count', fontsize=12)
        ax2.tick_params(axis='x', rotation=45)
        ax2.grid(True, alpha=0.3, axis='y')
        for i, v in enumerate(label_counts):
            ax2.text(i, v + 0.5, str(v), ha='center', va='bottom', fontweight='bold')
    else:
        ax2.text(0.5, 0.5, 'No labels applied', ha='center', va='center', fontsize=16, color='gray')
        ax2.set_title('Forecast Label Distribution', fontsize=14, fontweight='bold')
        ax2.set_xlim(0, 1)
        ax2.set_ylim(0, 1)

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=100, bbox_inches='tight')
        print(f"Plot saved to: {save_path}")
    else:
        save_path = None
    plt.show()
    return save_path


def plot_rain_results(csv_path):
    try:
        df = pd.read_csv(csv_path)
        return plot_rain_labeled_dataframe(df, save_path=csv_path.replace('.csv', '_rain_plot.png'))
    except Exception as e:
        print(f"Error plotting rain results: {e}")
        return None