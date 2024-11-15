# ASL Translation System

## Introduction
This project aims to build an American Sign Language (ASL) translation system that can recognize and translate 20 commonly used daily words. In addition to translating ASL, this system includes a functionality to test users' knowledge of ASL. This can be an excellent tool for both learning and practicing ASL.

## Features
- **Translation of ASL**: The system can translate 20 general daily used words from ASL to English.
- **Testing Knowledge**: Users can test their understanding and knowledge of ASL for the words included in the system.
- **Technologies Used**: The project is built using Python with the Tkinter library for the GUI components.

## Dataset
- **Data Collection**: Each of the 20 words is recorded 40 times to capture a range of expressions and nuances.
- **Data Storage**: The keypoints extracted from these recordings are stored in `.npy` files. There are 40 `.npy` files for each word, with each file representing a single recording session.

### Supported Words
The ASL translation system currently supports the following 20 commonly used daily words. These words were chosen for their frequency and utility in everyday communication:

|   Family   |   Friends   |   Work   |   School   |   Home   |   Car   |   Happy   |   Sad   |   Play   |   Help   |
|:----------:|:-----------:|:--------:|:----------:|:--------:|:-------:|:---------:|:-------:|:--------:|:--------:|
|    Eat     |    Drink    |   Sleep  |    Sorry   | Computer |  Money  |   Phone   |  Cloth  |    Me    |   Stop   |

## Models
Two models have been developed for this project:
- **LSTM Model**: Utilizes Long Short-Term Memory networks to analyze sequential data and predict translations.
- **CNN Model**: Employs Convolutional Neural Networks to interpret frame-based visual input from the ASL data.

## Database
- **SSMS**: SQL Server Management Studio (SSMS) is used for managing the database operations related to the storage of ASL data and user interactions.

## System Demonstration Video
[![Watch the video](https://img.youtube.com/vi/Vu4XojrXuPI/maxresdefault.jpg)](https://youtu.be/Vu4XojrXuPI?si=mkKx3yDBjFCPqzvR)
https://youtu.be/Vu4XojrXuPI


