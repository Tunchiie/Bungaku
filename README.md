## What audio features make a song a hit?

### Project Overview
Bungaku is a data analysis project focused on understanding how a song’s audio features relate to its chart performance. Using music data enriched with seasonal and decade-level context, the project explores whether features like loudness, tempo, and acousticness are statistically associated with a song’s likelihood of becoming a hit without using predictive modeling.

### Project Statement
The Billboard Hot 100 ranks the most popular songs each week based on radio play, streaming activity, and sales. Yet in the age of TikTok and algorithmic discovery, it has become harder to distinguish enduring hits from short-lived viral moments.

This project explores Billboard chart data from the past two decades to uncover which audio features are most strongly associated with hit songs. Rather than relying on inconsistent genre labels, the analysis focuses on quantifiable features such as tempo, loudness, and acousticness aiming to identify patterns across time and season that may explain chart success.

### Dataset
The dataset combines scraped Billboard Hot 100 chart data (2000–2025) with Spotify audio features obtained through the Spotify Web API. Each song includes metadata such as artist, track name, and chart rank, alongside numerical audio features like:

- Tempo

- Loudness

- Acousticness

- Speechiness

- Instrumentalness

For deeper analysis, additional fields were engineered — including season, decade, and hit status, defined by Top 10 appearance and chart longevity. Only tracks with valid dates and successfully matched Spotify audio features were included.

### Key Questions
- Which audio features most strongly correlate with a song becoming a hit?

- How do these relationships change across seasons (e.g., summer vs. winter)?

- Have feature trends in hit songs evolved over the past two decades?

- Are there feature value ranges (e.g., mid-tempo, moderate speechiness) where hit rates peak?

- Do hit songs differ significantly from non-hits based on statistical testing?

### Methodology
The analysis began with exploratory data analysis (EDA) on the full dataset to understand trends across audio features, label prevalence, artist frequency, and the characteristics of songs that consistently chart at the top or bottom of the Billboard Hot 100. This step provided a broad understanding of the dataset before splitting songs into hit and non-hit categories.
Songs were then labeled as "hits" or "non-hits" based on their Billboard chart performance, enabling comparative analysis. Relationships between features and hit status were explored using:
- Point Biserial Correlation and Mutual Information to capture both linear and non-linear associations
- T-tests to evaluate statistical differences between hit and non-hit feature distributions
- ANOVA and Tukey HSD to assess variation across seasons and decades

Visual tools such as violin plots, hit-rate binning charts, and z-score normalized heatmaps were used to highlight distribution shifts and feature interactions in a clear, interpretable format.

### Repository Structure
```text
bungaku/
├── data/
│   └── processed/                      # Final cleaned datasets used for analysis
│
├── notebooks/
│   ├── 03_EDA.ipynb                    # EDA: feature trends, label/artist frequency, seasonal and temporal context
│   └── 04_Feature_relationships.ipynb  # Statistical tests, binning, and feature-hit analysis
│
├── Images/                             # Saved plots (heatmaps, binning charts, violin plots, etc.)
├── requirements.txt                    # Project dependencies
├── .gitignore
└── README.md                           # Project overview and documentation
```

### Insights
---
#### Summary of Key EDA Insights
---
After exploring audio features across 130K+ Billboard Hot 100 entries, several patterns emerge about what defines a typical charting track:

##### Audio Characteristics of Charting Tracks
- **Tempo**: Most songs fall between **95–145 BPM**, clustering around **120 BPM**, a sweet spot for dancing and engagement.
- **Danceability**: Values typically range between **0.55 and 0.75**, suggesting charting songs are groovable but not overly dance-focused.
- **Energy**: High energy is a staple — most tracks fall between **0.6 and 0.85**, reflecting upbeat production.
- **Valence (Mood)**: Songs span both happy and sad moods, indicating no clear bias based on emotional tone.
- **Loudness**: Most tracks sit between **-7 and -4 dB**, favoring polished, loud studio production.
- **Speechiness**: The majority of songs have **low speechiness**, meaning they are sung rather than spoken.
- **Acousticness**: Tracks are overwhelmingly **digitally produced**, with purely acoustic songs being rare (likely reserved for live recordings).
- **Instrumentalness**: Hit songs are almost always **vocal-driven**; instrumental tracks are practically absent.
- **Liveness**: Most songs do **not** sound live, reinforcing a strong preference for clean, controlled studio production.

##### Musical Structure
- **Key**: Songs in **C, D, and G** dominate the charts. Other keys appear less frequently, likely due to vocal or instrumental constraints.
- **Time Signature**: **4/4** is overwhelmingly dominant — the rhythmic foundation of most Western pop music.

---

#### Summary of Feature Relationships and Seasonal Trends
This part of the project focused on how individual audio features relate to hit likelihood, and how those relationships shift across seasons and decades.

---

##### Feature Importance
- **Point Biserial Correlation** showed only weak linear relationships between features and hit status.
- **Mutual Information** captured non-linear dependencies more effectively:
  - Top-scoring features: `Tempo` (0.13), `Loudness` (0.11), followed by `Acousticness`, `Speechiness`, and `Instrumentalness`.

---

##### Statistical Testing
- **T-tests** confirmed statistically significant differences in the top 5 features between hit and non-hit songs, validating their relevance in chart performance.

---

##### Behavioral Patterns
- **Hit rate binning** revealed that certain feature value ranges (e.g., mid-range `loudness` and `speechiness`) are associated with a higher probability of becoming a hit.
- **Pairplots** showed low linear separability between hits and non-hits, suggesting that **feature combinations** matter more than individual values.

---

##### Temporal Variation
- **ANOVA by Decade** showed that:
  - `Acousticness`, `Speechiness`, and `Loudness` have shifted significantly across time.
  - Songs from the 2020s exhibit wider feature spread and variance.
- **Violin plots** revealed that:
  - Hit songs have become louder and more tightly clustered in `loudness`.
  - `Acousticness` and `Instrumentalness` have generally declined in modern hits.

---

##### Seasonal Trends
- **Seasonal ANOVA** identified significant variation in `Loudness` and `Acousticness` across seasons.
- **Tukey HSD** confirmed that **Winter** often differs significantly from other seasons for these features.
- **Z-score normalized heatmaps** visualized these shifts clearly:
  - **Winter** tracks tend to be quieter and more acoustic.
  - **Summer/Fall** tracks lean louder and more energetic.

---

#### Final Insight
No single feature defines a hit, but a **combination of feature values**, their **distribution over time**, and **seasonal context** all contribute to chart success. These insights form a strong foundation for future modeling and music behavior research.

## Future Work
This project focused purely on data analysis, without predictive modeling. Future extensions could include:

- Incorporating **artist** and **record label** metadata to assess external influence on chart success
- Building a **classification model** to predict hit status based on combined audio features and temporal context
- Expanding to include **lyrics sentiment** or **genre** for a more nuanced understanding of musical content
- Connecting music trends with **cultural shifts** by analyzing text-based data (e.g., from books, news, or social media) to align with the broader *Bungaku* vision


---
## Dependencies

```markdown
- `pandas`
- `numpy`
- `matplotlib`, `seaborn`
- `scikit-learn`
- `scipy`, `statsmodels`
- `spotipy`  *(for Spotify API-based feature matching)*
- `jupyter`
```

## Author

**Adetunji Fasiku**  
[LinkedIn](https://www.linkedin.com/in/adetunji-fasiku/) • [GitHub](https://github.com/tunchiie)2
