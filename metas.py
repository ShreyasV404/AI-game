import os
import datetime

def get_folder_metadata(folder_path):
    """Recursively gets metadata for all items in a folder."""
    metadata = {}
    if not os.path.exists(folder_path):
        print(f"Error: The folder '{folder_path}' does not exist.")
        return metadata

    for item_name in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item_name)
        try:
            item_stats = os.stat(item_path)
            item_metadata = {
                "Type": "Folder" if os.path.isdir(item_path) else "File",
                
            }

            if os.path.isdir(item_path):
                # Recursively get metadata for subfolders
                item_metadata["Contents"] = get_folder_metadata(item_path)
            
            metadata[item_name] = item_metadata
        except Exception as e:
            metadata[item_name] = {"Error": str(e)}

    return metadata

# Replace 'path/to/your/folder' with the actual folder path
folder_path = 'assets/tileset/'
all_metadata = get_folder_metadata(folder_path)

# Print or save the output
import json
# Convert the Python object to a formatted JSON string
json_string = json.dumps(all_metadata, indent=4)

# Define the filename for your text file
filename = "output_metadata.txt"

# Open the file in write mode ('w') and write the JSON string to it
with open(filename, 'w') as f:
    f.write(json_string)

print(f"JSON data saved to {filename}")