# Explanatory Visualization - NSF Terminated Grants Analysis
### *David González & Rebeca Torrecilla*
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B)
![Altair](https://img.shields.io/badge/Visualization-Altair-yellow)

The goal of this project is to create an explanatory visualization using **Altair** and **Streamlit** to analyze National Science Foundation (NSF) grants terminated during the Trump administration.

The analysis focuses on joining disparate datasets (terminated grants, Senator Ted Cruz's list, and flagged keywords) to understand the impact of these cancellations geographically, financially, and institutionally.

## Research Questions
This visualization project aims to answer the following key questions regarding the grant cancellations:

1.  **Geography:** How are the cancellations distributed by state?
2.  **Institutions (Count):** Which institutions have been most affected in terms of the *number* of cancelled grants?
3.  **Institutions (Budget):** Which institutions have been most affected in terms of *budget*, and how does this compare to others?
4.  **Flagged Words:** Is there any correlation between the cancelled grants and the list of "flagged" words potentially targeted by the administration?
5.  **Political Lists:** Is there any correlation between the cancelled grants and the list of grants in Senator Ted Cruz’s list? How does this compare to reinstated grants?

## Installation and Usage
To run this project locally you must ensure you have Python installed.

1. Clone the repository:
```
git clone https://github.com/rebecatorrecilla/Explanatory-Visualization.git
cd your-repo-name
```
2. Install dependencies (recommended a virtual environment)
```
pip install streamlit pandas altair numpy
```
3. Run the Streamlit Application in your terminal
```
streamlit run app.py
```
4. View the app: it will open automatically in your default web browser.

## Data Cleaning and Methodology
The data processing workflow is documented in detail in the ipynb file. The main steps included:
* **Data integration**: merging the terminated grants list with the Cruz list.
* **Cleaning***: handling missing values, repeated columns, standardizing names...
* **Augmentation**: claculating derived metrics to support visualization goals. 

## Visualization Design
The application is designed as a single-page explanatory dashboard.

* **Used Tools**: all charts were created using **Altair** to ensure consistency and interactivity.
* **Design Decisions**: detailed justifications for chart selection, color consistency and accessibility considerations are provided in the project report.
* **Interactivity**: the Streamlit application includes interactive elements to allow users to explore specific aspects of the data while maintaining a narrative flow.

## License
The project is developed for educational purposes within the Information Visualization course at UPC, Barcelona. 







