import os
import sys
import json
import re
import argparse
from datetime import datetime

def read_json_file(file_path):
    data = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()

        if content.startswith('"') and content.endswith('"'):
            content = content[1:-1]
            content = content.encode('utf-8').decode('unicode_escape')

        idx = 0
        content_length = len(content)
        decoder = json.JSONDecoder()

        while idx < content_length:
            try:
                obj, end_idx = decoder.raw_decode(content, idx)
                idx = end_idx
                if isinstance(obj, dict):
                    data.append(obj)
                elif isinstance(obj, list):
                    data.extend(obj)
                else:
                    print(f"Skipping non-dictionary JSON object at position {idx} in {file_path}.")
            except json.JSONDecodeError:
                idx += 1 
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return data

def process_data(data, file_path):
    html_content = ""
    url_pattern = re.compile(r'(https?://\S+)')

    for idx, message in enumerate(data):
        try:
            if not isinstance(message, dict):
                print(f"Skipping item at index {idx} in {file_path}: Not a dictionary.")
                continue

            author_id = message.get('author', 'Unknown')
            content = message.get('content', '')
            timestamp = message.get('timestamp', '')
            mentions = message.get('mentions', [])
            reactions = message.get('reaction_counts', {})

            if isinstance(timestamp, int):
                timestamp = datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')

            for mention in mentions:
                content = content.replace(f"<@{mention}>", f"<b>@{mention}</b>")

            content = url_pattern.sub(r'<a href="\1">\1</a>', content)

            if reactions:
                reactions_str = ' '.join([f"{emoji}: {count}" for emoji, count in reactions.items()])
                content += f"<br>Reactions: {reactions_str}"

            html_content += f"""
            <p>
                <b>{author_id}</b> [{timestamp}]:
                <br>
                {content}
            </p>
            <hr>
            """
        except Exception as e:
            print(f"Error processing message at index {idx} in {file_path}: {e}")
            continue

    return html_content

def convert_json_to_html(input_folder, output_folder):
    json_files = []
    for root, _, files in os.walk(input_folder):
        for file in files:
            if file.lower().endswith('.json'): 
                json_files.append(os.path.join(root, file))

    total_files = len(json_files)
    if total_files == 0:
        print("No JSON files found.")
        return

    for idx, json_file in enumerate(json_files):
        relative_path = os.path.relpath(json_file, input_folder)
        html_file = os.path.splitext(relative_path)[0] + '.html'
        output_file_path = os.path.join(output_folder, html_file)
        output_dir = os.path.dirname(output_file_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        data = read_json_file(json_file)
        if not data:
            print(f"No valid data found in {json_file}")
            continue
        content = process_data(data, json_file)

        try:
            with open(output_file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            print(f"Error writing HTML file {output_file_path}: {e}")
            continue

        progress = (idx + 1) / total_files * 100
        print(f"Processed {idx + 1}/{total_files} files ({progress:.2f}%)")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Batch convert JSON files to HTML.')
    parser.add_argument('input_folder', help='Input folder containing JSON files')
    parser.add_argument('output_folder', help='Output folder to save HTML files')

    args = parser.parse_args()

    convert_json_to_html(args.input_folder, args.output_folder)

# USAGE
# python .\json_to_html_converter.py "M:\Public Channels" "./html_output"

