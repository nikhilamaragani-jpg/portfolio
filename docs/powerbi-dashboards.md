# Power BI Dashboard Portfolio

The original dashboard PDF is available here: [Open or download the two-page Power BI dashboard PDF](../assets/powerbi-dashboards.pdf).

Both dashboards are described as learning/workshop projects. They are useful evidence of dashboard practice, but the supplied PDF does not include the source datasets, metric definitions, or project briefs. As a result, this document reports visible dashboard content without presenting it as verified business findings.

## Campfly Sales Analysis

**Portfolio description:** A Power BI sales dashboard exploring revenue and order quantity across years, products, customers, and channels.

Visible dashboard measures include total revenue (154.57M), average revenue (19.34K), and total unit cost (39.28K). It also includes year, product, customer, and channel views; visible customer labels include Medline, Eminence Corp, Apollo Ltd, Pure Group, and Victory Ltd.

The PDF does not state the revenue currency, data source, or calculation definitions for these figures. They are dashboard display values, not independently audited outcomes.

## Netflix Analysis

**Portfolio description:** A Power BI content dashboard exploring title catalogue size and content attributes.

Visible dashboard measures include 5,806 titles, 123M IMDb votes, an average IMDb rating of 6.53, and 451K runtime. The page includes views by release year, genre, age certification, and production country.

The PDF does not identify the underlying data source or explain whether the measures are counts, sums, or averages in every visual. Interpret the values as shown in the source dashboard, not verified conclusions.

## Improvement checklist for the original workshop reports

The supplied PDF is a static export. It does not contain the editable `.pbix` model or the source datasets, so I have preserved it as the original evidence rather than silently altering or recreating its figures. When those editable files are available, these are the first improvements to make:

### Campfly Sales Analysis

- Replace generic “Sum of …” titles with a short business question and clearly named measure.
- Review the goal/KPI cards and their target values; the exported card shows an unusually large goal variance that should be checked against the intended target and number format.
- Remove or relabel visuals whose axes use technical index/count fields unless those fields answer a defined business question.
- Define the revenue currency, date grain, order count, and meaning of average revenue in a visible subtitle or tooltip.
- Prioritize revenue, order count, units sold, gross profit/margin (only if cost data is validated), monthly trend, channel mix, and product/category comparison.
- Check sorting, blank product labels, duplicated order counting, and whether filters apply consistently across all charts.

### Netflix Content Analysis

- Validate whether “titles count” and “genres count” represent distinct titles and distinct genres; the PDF shows the same displayed total for both, so the measures should be checked.
- Confirm IMDb score measures use an average and remain on the expected 0–10 scale; verify the displayed average and any min/max values.
- Define runtime units and avoid summing runtimes unless the dashboard specifically intends total runtime.
- Make the chart labels and axes readable, and aggregate release-year/category visuals at a level that answers a clear content question.
- Distinguish missing ratings/certifications from zero values and document the source dataset and snapshot date.

These are review checks prompted by the export, not findings that the PBIX calculations are definitely wrong. Verify the data model and measures before changing them.

## Next steps to strengthen the projects

- Add the original dataset and its license/source citation.
- Document data types, missing values, and cleaning decisions.
- Define each KPI, its unit, and its aggregation.
- Write a few findings only after recalculating them from the underlying data.
- Add recommendations linked to validated findings.
- Add a PBIX file or an interactive Power BI link if available and safe to share.
