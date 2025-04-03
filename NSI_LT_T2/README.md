# Project: Geospatial Data Processing and Analysis for Emergency Shelter Detection

This repository contains Jupyter notebooks for processing geospatial data, segmenting orthophotographs, training deep learning models, and visualizing results. The workflows involve downloading remote sensing data, feature reduction, segmentation, embedding extraction, and anomaly detection.

## Table of Contents

- [Project Overview](#project-overview)
- [Notebooks Description](#notebooks-description)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Project Overview

This project processes and analyzes geospatial data, focusing on satellite imagery and orthophotos. The key components include:

- Downloading and processing orthophotos.
- Training a U-Net model for segmentation.
- Running a segmentation pipeline on processed orthophotos.
- Merging and filtering segmented data.
- Extracting embeddings for geospatial images.
- Reducing embedded features using autoencoders.
- Applying anomaly detection with Isolation Forest.

## Notebooks Description


### 1. `ortho_processing.ipynb`

**Description:** Downloads geospatial TIFF images from online geoportals based on tile numbers and dates. **Sources:**

- [Geoportal Lithuania](https://www.geoportal.lt/geoportal/)
- [Geoportaal Maaamet](https://geoportaal.maaamet.ee/eng/)

### 2. `unet_train.ipynb`

**Description:** Trains a Inception ResNet U-Net model for image segmentation on geospatial datasets (Inception ResNet UNet (Aghayari, S., Hadavand, A., Mohamadnezhad Niazi, S., & Omidalizarandi, M. (Year). Building Detection from Aerial Imagery Using Inception ResNet UNet and UNet Architectures. Retrieved from https://d-nb.info/1325796441/34))

### 3. `get_photo_embeds_for_vectors.ipynb`

**Description:** Uses ResNet-50 to extract embeddings from images corresponding to OpenStreetMap (OSM) features.

### 4. `segment_pipeline.ipynb`

**Description:** Implements a pipeline for segmenting and embedding geospatial TIFF images using the trained Inception ResNet U-Net model.

### 5. `merge_and_filter_segmented_data_geojsons.ipynb`

**Description:** Merges and filters segmented geospatial data stored in GeoJSON format together with OpenStreetMap data to prepare data for model.

### 6. `merge_all_data_for_model.ipynb`

**Description:** Merges target data to indicate which of the objects are currently used as emergency shelters.


### 7. `merge_all_data_for_model.ipynb`

**Description:** Reduces features using an autoencoder, applies Isolation Forest for anomaly detection, and computes additional statistics on the data.

### 8. `findme_shelter_dashboard.ipynb`

**Description:** Provides a dashboard for two NUTS 3 regions - EE001 (Estonia) and LT011 (Lithuania), using calculated shelter data.


## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/your-repo-name.git
   cd your-repo-name
   ```
2. Create a virtual environment (optional but recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run any of the Jupyter notebooks using:

```bash
jupyter notebook
```

Open the desired notebook and execute the cells sequentially.
For the whole pipeline, follow the notebooks in order as described in this document.

## Contributing

If you'd like to contribute, please submit a pull request or open an issue.

## License

This project is licensed under the MIT License. See `LICENSE` for details.


