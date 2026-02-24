# Model Comparison Report

## Why these models
All selected models are proven baselines for high-dimensional sparse text vectors (TF-IDF), covering linear, margin-based, tree-ensemble, and instance-based classification families.

## Metrics Comparison
| model | train_accuracy | test_accuracy | balanced_accuracy | precision_macro | recall_macro | f1_macro | precision_weighted | recall_weighted | f1_weighted | mcc | roc_auc_ovr_macro |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| logreg | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| svm | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| random_forest | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| xgboost | 1.0000 | 0.9922 | 0.9922 | 0.9927 | 0.9922 | 0.9923 | 0.9925 | 0.9922 | 0.9922 | 0.9914 | 1.0000 |
| knn | 1.0000 | 0.9883 | 0.9886 | 0.9886 | 0.9886 | 0.9884 | 0.9887 | 0.9883 | 0.9883 | 0.9870 | 1.0000 |
| decision_tree | 1.0000 | 0.9766 | 0.9766 | 0.9794 | 0.9766 | 0.9771 | 0.9789 | 0.9766 | 0.9768 | 0.9742 | 0.9870 |

## Model Rationales
- **logreg**: Strong linear baseline for sparse text; stable and interpretable coefficients with probabilistic outputs.
- **svm**: Effective margin-based classifier for text data, especially in high-dimensional TF-IDF spaces.
- **xgboost**: Powerful boosted-tree ensemble to capture non-linear patterns and feature interactions.
- **random_forest**: Bagged tree ensemble baseline with robustness against overfitting compared to single trees.
- **knn**: Instance-based non-parametric baseline to compare local-neighborhood behavior.
- **decision_tree**: Simple non-linear baseline with high interpretability.

## Selection Decision
Selected model: **logreg**

Selection reason: It achieved the highest macro F1 (1.0000). Tie-breakers were weighted F1, balanced accuracy, and test accuracy. If still tied, model preference favors stable linear models with reliable probability behavior.