import matplotlib.pyplot as plt
import pandas as pd
#POC MOCKUP

def plot_labeled_results(csv_path):
    """
    Plot visualization of labeled data.
    
    Args:
        csv_path (str): Path to the labeled CSV file
    """
    try:
        df = pd.read_csv(csv_path)
        
        # Create figure with subplots
        fig, axes = plt.subplots(2, 1, figsize=(12, 10))
        
        # Plot 1: PM2.5 and Temperature over time with label areas
        ax1 = axes[0]
        ax1.plot(df.index, df['PM2.5'], label='PM2.5', color='red', alpha=0.7, linewidth=2, zorder=3)
        ax1.set_ylabel('PM2.5 (μg/m³)', color='red', fontsize=12)
        ax1.tick_params(axis='y', labelcolor='red')
        ax1.set_xlabel('Row Index', fontsize=12)
        ax1.legend(loc='upper left', fontsize=10)
        ax1.grid(True, alpha=0.3)
        
        ax1_twin = ax1.twinx()
        ax1_twin.plot(df.index, df['Temp'], label='Temperature', color='blue', alpha=0.7, linewidth=2, zorder=3)
        ax1_twin.set_ylabel('Temperature (°C)', color='blue', fontsize=12)
        ax1_twin.tick_params(axis='y', labelcolor='blue')
        ax1_twin.legend(loc='upper right', fontsize=10)
        
        # Find continuous labeled regions
        labeled_rows = df[df['auto_label'].notna() & (df['auto_label'] != '')]
        
        # Get unique labels and assign colors
        unique_labels = labeled_rows['auto_label'].unique()
        label_colors = plt.cm.tab10(range(len(unique_labels)))
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
                    
                    # Add annotation at middle of region
                    ax1.annotate(label_text,
                                xy=(mid_idx, pm_value),
                                xytext=(0, 30),
                                textcoords='offset points',
                                fontsize=9,
                                color='white',
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
            colors = plt.cm.Set3(range(len(label_counts)))
            label_counts.plot(kind='bar', ax=ax2, color=colors, edgecolor='black', linewidth=1.2)
            ax2.set_title('Label Distribution', fontsize=14, fontweight='bold')
            ax2.set_xlabel('Labels', fontsize=12)
            ax2.set_ylabel('Count', fontsize=12)
            ax2.tick_params(axis='x', rotation=45)
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
