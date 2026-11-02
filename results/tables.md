# NetShift-IDS experiment tables

Generated from `results/results_log.csv`; no metrics are recomputed here.

| experiment | model | selection | feature_set | label_budget | rows | seeds | n_train | n_test | n_labelled_target | macro_f1_mean | macro_f1_std | mcc_mean | mcc_std | majority_caps | smote_caps |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| baseline | rf | none | all | 0.0 | 3 | 3 | 1925791.0 | 481448.0 | 0.0 | 0.9513 | 0.0022 | 0.9954 | 0.0001 | 200000 | 50000 |
| baseline | xgboost | none | all | 0.0 | 3 | 3 | 1925791.0 | 481448.0 | 0.0 | 0.9543 | 0.0022 | 0.9967 | 0.0002 | 200000 | 50000 |
| cross_network | rf | none | all | 0.0 | 3 | 3 | 2407239.0 | 11306601.0 | 0.0 | 0.1917 | 0.0016 | 0.1262 | 0.0043 | 200000 | 50000 |
| cross_network | xgboost | none | all | 0.0 | 3 | 3 | 2407239.0 | 11306601.0 | 0.0 | 0.4936 | 0.0066 | 0.5672 | 0.0131 | 200000 | 50000 |
| label_budget | rf | random | all | 0.0 | 3 | 3 | 2407239.0 | 5653300.0 | 0.0 | 0.1916 | 0.0017 | 0.126 | 0.0045 | 200000 | 50000 |
| label_budget | rf | random | all | 0.01 | 3 | 3 | 2463772.0 | 5653300.0 | 56533.0 | 0.8597 | 0.0287 | 0.9923 | 0.0008 | 200000 | 50000 |
| label_budget | rf | random | all | 0.05 | 3 | 3 | 2689904.0 | 5653300.0 | 282665.0 | 0.8801 | 0.0115 | 0.9953 | 0.0007 | 200000 | 50000 |
| label_budget | rf | random | all | 0.1 | 3 | 3 | 2972569.0 | 5653300.0 | 565330.0 | 0.8802 | 0.003 | 0.996 | 0.0004 | 200000 | 50000 |
| label_budget | rf | random | shortcut_removed | 0.0 | 3 | 3 | 2407239.0 | 5653300.0 | 0.0 | 0.1943 | 0.014 | 0.2312 | 0.0123 | 200000 | 50000 |
| label_budget | rf | random | shortcut_removed | 0.01 | 3 | 3 | 2463772.0 | 5653300.0 | 56533.0 | 0.8708 | 0.0121 | 0.9921 | 0.0007 | 200000 | 50000 |
| label_budget | rf | random | shortcut_removed | 0.05 | 3 | 3 | 2689904.0 | 5653300.0 | 282665.0 | 0.8805 | 0.0106 | 0.9953 | 0.0006 | 200000 | 50000 |
| label_budget | rf | random | shortcut_removed | 0.1 | 3 | 3 | 2972569.0 | 5653300.0 | 565330.0 | 0.8817 | 0.0041 | 0.9965 | 0.0004 | 200000 | 50000 |
| label_budget | xgboost | random | all | 0.0 | 3 | 3 | 2407239.0 | 5653300.0 | 0.0 | 0.494 | 0.0068 | 0.5673 | 0.0132 | 200000 | 50000 |
| label_budget | xgboost | random | all | 0.01 | 3 | 3 | 2463772.0 | 5653300.0 | 56533.0 | 0.8963 | 0.0576 | 0.997 | 0.0018 | 200000 | 50000 |
| label_budget | xgboost | random | all | 0.05 | 3 | 3 | 2689904.0 | 5653300.0 | 282665.0 | 0.884 | 0.0407 | 0.9963 | 0.0022 | 200000 | 50000 |
| label_budget | xgboost | random | all | 0.1 | 3 | 3 | 2972569.0 | 5653300.0 | 565330.0 | 0.8665 | 0.0025 | 0.9964 | 0.0001 | 200000 | 50000 |
| label_budget | xgboost | random | shortcut_removed | 0.0 | 3 | 3 | 2407239.0 | 5653300.0 | 0.0 | 0.4067 | 0.0621 | 0.3355 | 0.061 | 200000 | 50000 |
| label_budget | xgboost | random | shortcut_removed | 0.01 | 3 | 3 | 2463772.0 | 5653300.0 | 56533.0 | 0.891 | 0.0556 | 0.9966 | 0.0014 | 200000 | 50000 |
| label_budget | xgboost | random | shortcut_removed | 0.05 | 3 | 3 | 2689904.0 | 5653300.0 | 282665.0 | 0.8786 | 0.0333 | 0.996 | 0.0025 | 200000 | 50000 |
| label_budget | xgboost | random | shortcut_removed | 0.1 | 3 | 3 | 2972569.0 | 5653300.0 | 565330.0 | 0.8643 | 0.0044 | 0.9962 | 0.0005 | 200000 | 50000 |
| label_budget_uncertainty | rf | uncertainty | all | 0.0 | 3 | 3 | 2407239.0 | 5653300.0 | 0.0 | 0.1916 | 0.0017 | 0.126 | 0.0045 | 200000 | 50000 |
| label_budget_uncertainty | rf | uncertainty | all | 0.01 | 3 | 3 | 2463772.0 | 5653300.0 | 56533.0 | 0.3758 | 0.0384 | 0.4002 | 0.1381 | 200000 | 50000 |
| label_budget_uncertainty | rf | uncertainty | all | 0.05 | 3 | 3 | 2689904.0 | 5653300.0 | 282665.0 | 0.5024 | 0.0688 | 0.6863 | 0.0288 | 200000 | 50000 |
| label_budget_uncertainty | rf | uncertainty | all | 0.1 | 3 | 3 | 2972569.0 | 5653300.0 | 565330.0 | 0.8088 | 0.0138 | 0.9025 | 0.0307 | 200000 | 50000 |
| label_budget_uncertainty | xgboost | uncertainty | all | 0.0 | 3 | 3 | 2407239.0 | 5653300.0 | 0.0 | 0.494 | 0.0068 | 0.5673 | 0.0132 | 200000 | 50000 |
| label_budget_uncertainty | xgboost | uncertainty | all | 0.01 | 3 | 3 | 2463772.0 | 5653300.0 | 56533.0 | 0.7414 | 0.0004 | 0.7516 | 0.0006 | 200000 | 50000 |
| label_budget_uncertainty | xgboost | uncertainty | all | 0.05 | 3 | 3 | 2689904.0 | 5653300.0 | 282665.0 | 0.8415 | 0.052 | 0.8033 | 0.0686 | 200000 | 50000 |
| label_budget_uncertainty | xgboost | uncertainty | all | 0.1 | 3 | 3 | 2972569.0 | 5653300.0 | 565330.0 | 0.8478 | 0.0213 | 0.8794 | 0.0166 | 200000 | 50000 |
| shortcut_removed | rf | none | shortcut_removed | 0.0 | 3 | 3 | 2407239.0 | 11306601.0 | 0.0 | 0.1947 | 0.0142 | 0.2315 | 0.0123 | 200000 | 50000 |
| shortcut_removed | xgboost | none | shortcut_removed | 0.0 | 3 | 3 | 2407239.0 | 11306601.0 | 0.0 | 0.4068 | 0.0623 | 0.3354 | 0.061 | 200000 | 50000 |
