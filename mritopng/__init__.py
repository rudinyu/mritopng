import os
import png
import dicom


def extract_grayscale_image(mri_file):
    # Extracting data from the mri file
    plan = dicom.read_file(mri_file)
    shape = plan.pixel_array.shape

    image_2d = []
    max_val = 0
    for row in plan.pixel_array:
        pixels = []
        for col in row:
            pixels.append(col)
            if col > max_val:
                max_val = col
        image_2d.append(pixels)

    # Rescaling grey scale between 0-255
    image_2d_scaled = []
    for row in image_2d:
        row_scaled = []
        for col in row:
            # cliping pixel value if below 0
            col_scaled = int((float(max(col, 0)) / float(max_val)) * 255.0)
            row_scaled.append(col_scaled)
        image_2d_scaled.append(row_scaled)
    
    return image_2d_scaled


def mri_to_png(mri_file, png_file):
    """ Function to convert from a DICOM image to png

        @param mri_file: An opened file like object to read te dicom data
        @param png_file: An opened file like object to write the png data
    """

    image_2d_scaled = extract_grayscale_image(mri_file)

    # Writing the PNG file
    w = png.Writer(len(image_2d_scaled[0]), len(image_2d_scaled), greyscale=True)
    w.write(png_file, image_2d_scaled)


def convert_file(mri_file_path, png_file_path):
    """ Function to convert an MRI binary file to a
        PNG image file.

        @param mri_file_path: Full path to the mri file
        @param png_file_path: Fill path to the png file
    """

    # Making sure that the mri file exists
    if not os.path.exists(mri_file_path):
        raise Exception('File "%s" does not exists' % mri_file_path)

    # Making sure the png file does not exist
    if os.path.exists(png_file_path):
        raise Exception('File "%s" already exists' % png_file_path)

    mri_file = open(mri_file_path, 'rb')
    png_file = open(png_file_path, 'wb')

    mri_to_png(mri_file, png_file)

    png_file.close()


def convert_folder(mri_folder, png_folder):
    """ Convert all MRI files in a folder to png files
        in a destination folder
    """

    # Create the folder for the pnd directory structure
    os.makedirs(png_folder)

    # Recursively traverse all sub-folders in the path
    for mri_sub_folder, subdirs, files in os.walk(mri_folder):
        for mri_file in os.listdir(mri_sub_folder):
            mri_file_path = os.path.join(mri_sub_folder, mri_file)

            # Make sure path is an actual file
            if os.path.isfile(mri_file_path):

                # Replicate the original file structure
                rel_path = os.path.relpath(mri_sub_folder, mri_folder)
                png_folder_path = os.path.join(png_folder, rel_path)
                if not os.path.exists(png_folder_path):
                    os.makedirs(png_folder_path)
                png_file_path = os.path.join(png_folder_path, '%s.png' % mri_file)

                try:
                    # Convert the actual file
                    convert_file(mri_file_path, png_file_path)
                    print('SUCCESS: %s --> %s' % (mri_file_path, png_file_path))
                except Exception as e:
                    print('FAIL: %s --> %s : %s' % (mri_file_path, png_file_path, e))
