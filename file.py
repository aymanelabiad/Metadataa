import os
import tempfile
import streamlit as st
import subprocess
from zipfile import ZipFile

# Streamlit Web App
st.title("Bulk Video Metadata Removal Tool")
st.write("Upload multiple videos, and this tool will remove their metadata.")

# File upload section
uploaded_files = st.file_uploader(
    "Upload your video files (you can upload multiple files)", 
    type=["mp4", "mov", "avi", "mkv"], 
    accept_multiple_files=True
)

# Determine the path to exiftool.exe based on where the script is running
# Assuming exiftool.exe is in the 'exiftool_files' folder in your repo
exiftool_path = os.path.join(os.path.dirname(__file__), "exiftool_files", "exiftool.exe")

if uploaded_files:
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        cleaned_files = []
        
        # Process each uploaded file
        for uploaded_file in uploaded_files:
            input_file_path = os.path.join(temp_dir, uploaded_file.name)
            
            # Save uploaded file to the temp directory
            with open(input_file_path, "wb") as f:
                f.write(uploaded_file.read())
            
            # Output file path
            output_file_path = os.path.join(temp_dir, f"cleaned_{uploaded_file.name}")
            
            # Remove metadata using ExifTool via subprocess
            try:
                subprocess.run(
                    [exiftool_path, "-all=", "-o", output_file_path, input_file_path],
                    check=True
                )
                cleaned_files.append(output_file_path)
            except subprocess.CalledProcessError as e:
                st.error(f"An error occurred while processing {uploaded_file.name}: {e}")
        
        if cleaned_files:
            # Provide individual download links
            st.success(f"Metadata has been removed from {len(cleaned_files)} videos successfully!")
            for cleaned_file in cleaned_files:
                with open(cleaned_file, "rb") as f:
                    cleaned_video = f.read()
                st.download_button(
                    label=f"Download Cleaned Video: {os.path.basename(cleaned_file)}",
                    data=cleaned_video,
                    file_name=os.path.basename(cleaned_file),
                    mime="video/mp4"
                )
            
            # Optionally, provide all files in a ZIP archive
            zip_file_path = os.path.join(temp_dir, "cleaned_videos.zip")
            with ZipFile(zip_file_path, "w") as zipf:
                for cleaned_file in cleaned_files:
                    zipf.write(cleaned_file, arcname=os.path.basename(cleaned_file))
            
            with open(zip_file_path, "rb") as zf:
                st.download_button(
                    label="Download All Cleaned Videos (ZIP)",
                    data=zf.read(),
                    file_name="cleaned_videos.zip",
                    mime="application/zip"
                )
