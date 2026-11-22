## E1. AUROC by amplified share (full cascades)

| π target | π realised | size only | shape | branching | timing | reuse | structure + timing | all | all: recall at 1% FPR |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2% | 3.5% | 0.497 ± 0.031 | 0.539 ± 0.018 | 0.528 ± 0.031 | 0.611 ± 0.028 | 0.544 ± 0.028 | 0.624 ± 0.029 | 0.633 ± 0.029 | 0.03 ± 0.01 |
| 5% | 5.2% | 0.528 ± 0.020 | 0.580 ± 0.021 | 0.562 ± 0.017 | 0.735 ± 0.024 | 0.700 ± 0.021 | 0.756 ± 0.018 | 0.802 ± 0.011 | 0.21 ± 0.03 |
| 10% | 9.4% | 0.530 ± 0.039 | 0.645 ± 0.027 | 0.619 ± 0.036 | 0.893 ± 0.013 | 0.910 ± 0.010 | 0.905 ± 0.015 | 0.947 ± 0.006 | 0.58 ± 0.06 |
| 15% | 14.0% | 0.554 ± 0.017 | 0.710 ± 0.020 | 0.680 ± 0.012 | 0.942 ± 0.009 | 0.986 ± 0.005 | 0.952 ± 0.008 | 0.992 ± 0.003 | 0.89 ± 0.05 |
| 20% | 18.1% | 0.570 ± 0.044 | 0.759 ± 0.023 | 0.740 ± 0.023 | 0.954 ± 0.007 | 0.996 ± 0.001 | 0.968 ± 0.006 | 0.997 ± 0.001 | 0.97 ± 0.01 |
| 30% | 25.8% | 0.614 ± 0.016 | 0.841 ± 0.017 | 0.832 ± 0.021 | 0.964 ± 0.004 | 1.000 ± 0.000 | 0.986 ± 0.002 | 1.000 ± 0.000 | 1.00 ± 0.00 |
| 40% | 32.8% | 0.648 ± 0.028 | 0.897 ± 0.015 | 0.897 ± 0.015 | 0.968 ± 0.005 | 1.000 ± 0.000 | 0.994 ± 0.002 | 1.000 ± 0.000 | 1.00 ± 0.00 |
| 60% | 44.0% | 0.773 ± 0.024 | 0.971 ± 0.005 | 0.965 ± 0.005 | 0.980 ± 0.002 | 1.000 ± 0.000 | 0.998 ± 0.001 | 1.000 ± 0.000 | 1.00 ± 0.00 |

## E2. AUROC by reshares seen

| Features | π | first 5 | first 10 | first 20 | first 50 | first 100 | all |
| --- | --- | --- | --- | --- | --- | --- | --- |
| structure + timing | 5% | 0.751 ± 0.027 | 0.765 ± 0.030 | 0.762 ± 0.023 | 0.765 ± 0.017 | 0.760 ± 0.021 | 0.756 ± 0.018 |
| structure + timing | 10% | 0.837 ± 0.014 | 0.852 ± 0.019 | 0.870 ± 0.016 | 0.885 ± 0.013 | 0.899 ± 0.015 | 0.905 ± 0.015 |
| structure + timing | 20% | 0.938 ± 0.004 | 0.953 ± 0.006 | 0.963 ± 0.004 | 0.966 ± 0.007 | 0.966 ± 0.005 | 0.968 ± 0.006 |
| structure + timing | 40% | 0.964 ± 0.003 | 0.994 ± 0.001 | 0.994 ± 0.002 | 0.995 ± 0.002 | 0.994 ± 0.002 | 0.994 ± 0.002 |
| reuse | 5% | 0.957 ± 0.007 | 0.938 ± 0.008 | 0.802 ± 0.022 | 0.748 ± 0.013 | 0.726 ± 0.018 | 0.700 ± 0.021 |
| reuse | 10% | 0.965 ± 0.009 | 0.970 ± 0.004 | 0.912 ± 0.011 | 0.884 ± 0.019 | 0.902 ± 0.011 | 0.910 ± 0.010 |
| reuse | 20% | 0.967 ± 0.007 | 0.992 ± 0.004 | 0.995 ± 0.001 | 0.993 ± 0.002 | 0.995 ± 0.001 | 0.996 ± 0.001 |
| reuse | 40% | 0.965 ± 0.010 | 0.993 ± 0.004 | 0.999 ± 0.001 | 1.000 ± 0.000 | 1.000 ± 0.000 | 1.000 ± 0.000 |
| all | 5% | 0.961 ± 0.008 | 0.902 ± 0.013 | 0.851 ± 0.016 | 0.840 ± 0.010 | 0.828 ± 0.011 | 0.802 ± 0.011 |
| all | 10% | 0.977 ± 0.003 | 0.955 ± 0.006 | 0.945 ± 0.008 | 0.946 ± 0.006 | 0.946 ± 0.006 | 0.947 ± 0.006 |
| all | 20% | 0.989 ± 0.003 | 0.994 ± 0.002 | 0.996 ± 0.001 | 0.996 ± 0.001 | 0.997 ± 0.001 | 0.997 ± 0.001 |
| all | 40% | 0.990 ± 0.002 | 0.999 ± 0.001 | 1.000 ± 0.000 | 1.000 ± 0.000 | 1.000 ± 0.000 | 1.000 ± 0.000 |

## E3. AUROC by organic mean offspring m

| π | Features | m = 0.5 | m = 0.65 | m = 0.8 | m = 0.9 | m = 0.95 |
| --- | --- | --- | --- | --- | --- | --- |
| 10% | size only | 0.560 ± 0.025 | 0.548 ± 0.027 | 0.530 ± 0.039 | 0.535 ± 0.021 | 0.534 ± 0.035 |
| 10% | structure + timing | 0.790 ± 0.017 | 0.855 ± 0.012 | 0.905 ± 0.015 | 0.932 ± 0.008 | 0.945 ± 0.006 |
| 10% | reuse | 0.791 ± 0.017 | 0.843 ± 0.019 | 0.910 ± 0.010 | 0.956 ± 0.006 | 0.974 ± 0.005 |
| 10% | all | 0.871 ± 0.014 | 0.913 ± 0.008 | 0.947 ± 0.006 | 0.970 ± 0.004 | 0.982 ± 0.003 |
| 30% | size only | 0.658 ± 0.026 | 0.631 ± 0.042 | 0.614 ± 0.016 | 0.578 ± 0.017 | 0.582 ± 0.029 |
| 30% | structure + timing | 0.963 ± 0.006 | 0.977 ± 0.007 | 0.986 ± 0.002 | 0.988 ± 0.004 | 0.990 ± 0.003 |
| 30% | reuse | 1.000 ± 0.001 | 1.000 ± 0.000 | 1.000 ± 0.000 | 0.999 ± 0.001 | 0.998 ± 0.001 |
| 30% | all | 1.000 ± 0.000 | 1.000 ± 0.000 | 1.000 ± 0.000 | 1.000 ± 0.000 | 1.000 ± 0.000 |

## E4. Evasion strategies (full cascades)

| π | Strategy | Size only | Structure + timing | Reuse | All | All: recall at 1% FPR | All, trained on naive only |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 10% | naive | 0.530 ± 0.039 | 0.905 ± 0.015 | 0.910 ± 0.010 | 0.947 ± 0.006 | 0.58 ± 0.06 | 0.950 ± 0.007 |
| 10% | random timing | 0.530 ± 0.039 | 0.906 ± 0.015 | 0.910 ± 0.010 | 0.947 ± 0.006 | 0.60 ± 0.06 | 0.951 ± 0.007 |
| 10% | organic timing | 0.535 ± 0.033 | 0.662 ± 0.022 | 0.916 ± 0.013 | 0.921 ± 0.009 | 0.50 ± 0.03 | 0.876 ± 0.011 |
| 10% | organic timing + structure | 0.539 ± 0.020 | 0.659 ± 0.022 | 0.914 ± 0.006 | 0.913 ± 0.008 | 0.50 ± 0.04 | 0.831 ± 0.019 |
| 10% | full mimic + rotation | 0.533 ± 0.024 | 0.652 ± 0.019 | 0.539 ± 0.014 | 0.658 ± 0.018 | 0.04 ± 0.02 | 0.454 ± 0.031 |
| 10% | control: embedded accounts | 0.506 ± 0.029 | 0.494 ± 0.023 | 0.914 ± 0.010 | 0.906 ± 0.010 | 0.47 ± 0.04 | 0.839 ± 0.017 |
| 30% | naive | 0.614 ± 0.016 | 0.986 ± 0.002 | 1.000 ± 0.000 | 1.000 ± 0.000 | 1.00 ± 0.00 | 1.000 ± 0.000 |
| 30% | random timing | 0.614 ± 0.016 | 0.991 ± 0.002 | 1.000 ± 0.000 | 1.000 ± 0.000 | 1.00 ± 0.00 | 1.000 ± 0.000 |
| 30% | organic timing | 0.605 ± 0.033 | 0.847 ± 0.014 | 1.000 ± 0.000 | 0.999 ± 0.001 | 0.99 ± 0.00 | 0.999 ± 0.001 |
| 30% | organic timing + structure | 0.605 ± 0.035 | 0.892 ± 0.013 | 1.000 ± 0.000 | 1.000 ± 0.000 | 1.00 ± 0.00 | 0.999 ± 0.001 |
| 30% | full mimic + rotation | 0.612 ± 0.032 | 0.901 ± 0.009 | 0.694 ± 0.028 | 0.906 ± 0.010 | 0.34 ± 0.10 | 0.572 ± 0.052 |
| 30% | control: embedded accounts | 0.483 ± 0.044 | 0.508 ± 0.028 | 1.000 ± 0.000 | 1.000 ± 0.000 | 1.00 ± 0.00 | 1.000 ± 0.000 |

First 20 reshares only:

| π | Strategy | Structure + timing | Reuse | All |
| --- | --- | --- | --- | --- |
| 10% | naive | 0.870 ± 0.016 | 0.912 ± 0.011 | 0.945 ± 0.008 |
| 10% | random timing | 0.882 ± 0.015 | 0.911 ± 0.012 | 0.946 ± 0.008 |
| 10% | organic timing | 0.650 ± 0.030 | 0.870 ± 0.016 | 0.874 ± 0.015 |
| 10% | organic timing + structure | 0.553 ± 0.022 | 0.597 ± 0.017 | 0.627 ± 0.029 |
| 10% | full mimic + rotation | 0.550 ± 0.030 | 0.508 ± 0.027 | 0.545 ± 0.033 |
| 10% | control: embedded accounts | 0.496 ± 0.021 | 0.679 ± 0.033 | 0.673 ± 0.024 |
| 30% | naive | 0.984 ± 0.003 | 1.000 ± 0.001 | 1.000 ± 0.000 |
| 30% | random timing | 0.989 ± 0.002 | 0.999 ± 0.001 | 1.000 ± 0.000 |
| 30% | organic timing | 0.803 ± 0.013 | 0.997 ± 0.003 | 0.999 ± 0.001 |
| 30% | organic timing + structure | 0.708 ± 0.024 | 0.862 ± 0.018 | 0.911 ± 0.015 |
| 30% | full mimic + rotation | 0.722 ± 0.023 | 0.596 ± 0.022 | 0.740 ± 0.021 |
| 30% | control: embedded accounts | 0.515 ± 0.023 | 0.971 ± 0.006 | 0.975 ± 0.005 |

## E4. What each strategy costs the attacker

| π | Strategy | Minutes until 90% of amplifier reshares land | Amplifier reshares in first hour | Accounts used per campaign | Cascades per account | Reshares in first hour, amplified | Reshares in first hour, organic |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 10% | naive | 7 | 100% | 40 | 7.5 | 22.9 | 14.4 |
| 10% | random timing | 7 | 100% | 40 | 7.5 | 22.9 | 14.4 |
| 10% | organic timing | 122 | 67% | 39 | 7.8 | 20.0 | 14.4 |
| 10% | organic timing + structure | 444 | 16% | 37 | 8.0 | 15.1 | 14.4 |
| 10% | full mimic + rotation | 445 | 16% | 283 | 1.0 | 14.8 | 14.4 |
| 10% | control: embedded accounts | 323 | 30% | 35 | 7.6 | 14.3 | 14.4 |
| 30% | naive | 11 | 100% | 128 | 8.8 | 46.5 | 14.4 |
| 30% | random timing | 11 | 100% | 128 | 8.8 | 46.5 | 14.4 |
| 30% | organic timing | 178 | 63% | 126 | 8.8 | 33.4 | 14.4 |
| 30% | organic timing + structure | 536 | 15% | 122 | 9.1 | 17.3 | 14.4 |
| 30% | full mimic + rotation | 529 | 15% | 1029 | 1.1 | 17.3 | 14.4 |
| 30% | control: embedded accounts | 409 | 31% | 101 | 8.1 | 14.6 | 14.4 |

## E4b. Account rotation under the full-mimic strategy (π = 20%)

| Pool size per campaign | Accounts actually used | Cascades per account | Reuse AUROC | All AUROC |
| --- | --- | --- | --- | --- |
| 50 | 50 | 11.78 | 0.982 ± 0.004 | 0.989 ± 0.003 |
| 150 | 149 | 4.49 | 0.956 ± 0.009 | 0.975 ± 0.007 |
| 500 | 375 | 1.80 | 0.763 ± 0.012 | 0.859 ± 0.014 |
| 2,000 | 581 | 1.18 | 0.585 ± 0.023 | 0.805 ± 0.019 |
| 10,000 | 645 | 1.03 | 0.632 ± 0.019 | 0.820 ± 0.016 |

## E4c. Late start of a naive campaign (π = 20%)

| Start delay | View | Structure + timing | Reuse | All |
| --- | --- | --- | --- | --- |
| 5 min | first 20 | 0.963 ± 0.004 | 0.995 ± 0.001 | 0.996 ± 0.001 |
| 5 min | all | 0.968 ± 0.006 | 0.996 ± 0.001 | 0.997 ± 0.001 |
| 60 min | first 20 | 0.821 ± 0.011 | 0.843 ± 0.023 | 0.916 ± 0.010 |
| 60 min | all | 0.908 ± 0.006 | 0.996 ± 0.001 | 0.996 ± 0.001 |
| 360 min | first 20 | 0.677 ± 0.016 | 0.678 ± 0.019 | 0.735 ± 0.013 |
| 360 min | all | 0.980 ± 0.004 | 0.996 ± 0.001 | 0.998 ± 0.001 |

## E5. Base rate (π = 10%, 200 amplified cascades)

| Strategy | Amplified share of corpus | Features | AUROC | Average precision | Recall at 1% FPR |
| --- | --- | --- | --- | --- | --- |
| naive | 50% | structure + timing | 0.890 ± 0.021 | 0.891 ± 0.023 | 0.34 ± 0.12 |
| naive | 50% | reuse | 0.954 ± 0.009 | 0.957 ± 0.009 | 0.58 ± 0.11 |
| naive | 50% | all | 0.962 ± 0.007 | 0.966 ± 0.008 | 0.68 ± 0.11 |
| naive | 10% | structure + timing | 0.901 ± 0.012 | 0.656 ± 0.036 | 0.39 ± 0.05 |
| naive | 10% | reuse | 0.964 ± 0.009 | 0.880 ± 0.024 | 0.75 ± 0.05 |
| naive | 10% | all | 0.967 ± 0.005 | 0.893 ± 0.016 | 0.78 ± 0.03 |
| naive | 2% | structure + timing | 0.880 ± 0.015 | 0.422 ± 0.033 | 0.41 ± 0.04 |
| naive | 2% | reuse | 0.960 ± 0.009 | 0.846 ± 0.013 | 0.82 ± 0.02 |
| naive | 2% | all | 0.969 ± 0.007 | 0.849 ± 0.010 | 0.83 ± 0.01 |
| organic timing + structure | 50% | structure + timing | 0.638 ± 0.029 | 0.632 ± 0.025 | 0.04 ± 0.02 |
| organic timing + structure | 50% | reuse | 0.952 ± 0.010 | 0.957 ± 0.008 | 0.61 ± 0.06 |
| organic timing + structure | 50% | all | 0.942 ± 0.010 | 0.947 ± 0.010 | 0.56 ± 0.09 |
| organic timing + structure | 10% | structure + timing | 0.624 ± 0.026 | 0.175 ± 0.025 | 0.04 ± 0.02 |
| organic timing + structure | 10% | reuse | 0.967 ± 0.007 | 0.881 ± 0.015 | 0.73 ± 0.02 |
| organic timing + structure | 10% | all | 0.963 ± 0.008 | 0.868 ± 0.019 | 0.73 ± 0.03 |
| organic timing + structure | 2% | structure + timing | 0.624 ± 0.026 | 0.049 ± 0.008 | 0.05 ± 0.01 |
| organic timing + structure | 2% | reuse | 0.957 ± 0.006 | 0.835 ± 0.021 | 0.82 ± 0.03 |
| organic timing + structure | 2% | all | 0.959 ± 0.008 | 0.819 ± 0.017 | 0.80 ± 0.02 |
| full mimic + rotation | 50% | structure + timing | 0.633 ± 0.037 | 0.623 ± 0.032 | 0.03 ± 0.01 |
| full mimic + rotation | 50% | reuse | 0.533 ± 0.025 | 0.533 ± 0.025 | 0.02 ± 0.02 |
| full mimic + rotation | 50% | all | 0.641 ± 0.030 | 0.622 ± 0.027 | 0.02 ± 0.02 |
| full mimic + rotation | 10% | structure + timing | 0.628 ± 0.017 | 0.188 ± 0.024 | 0.05 ± 0.02 |
| full mimic + rotation | 10% | reuse | 0.552 ± 0.030 | 0.129 ± 0.013 | 0.02 ± 0.01 |
| full mimic + rotation | 10% | all | 0.641 ± 0.012 | 0.200 ± 0.023 | 0.06 ± 0.03 |
| full mimic + rotation | 2% | structure + timing | 0.617 ± 0.027 | 0.044 ± 0.008 | 0.06 ± 0.01 |
| full mimic + rotation | 2% | reuse | 0.591 ± 0.021 | 0.034 ± 0.010 | 0.03 ± 0.02 |
| full mimic + rotation | 2% | all | 0.642 ± 0.019 | 0.057 ± 0.015 | 0.07 ± 0.02 |

## E6. Sensitivity: AUROC (all features) with one parameter moved from its default

| Parameter | Value | naive, π = 10% | organic timing + structure, π = 10% | full mimic + rotation, π = 30% |
| --- | --- | --- | --- | --- |
| All at default | | 0.947 ± 0.006 | 0.913 ± 0.008 | 0.906 ± 0.010 |
| Direct reshares of the post (default 6) | 3 | 0.921 ± 0.009 | 0.860 ± 0.013 | 0.883 ± 0.006 |
| Direct reshares of the post (default 6) | 12 | 0.973 ± 0.005 | 0.961 ± 0.005 | 0.931 ± 0.006 |
| Spread of reaction delays (default 1.3) | 0.8 | 0.959 ± 0.007 | 0.912 ± 0.009 | 0.906 ± 0.010 |
| Spread of reaction delays (default 1.3) | 1.8 | 0.938 ± 0.008 | 0.914 ± 0.007 | 0.905 ± 0.012 |
| Reactions per amplifier reshare (default 0.15) | 0 | 0.958 ± 0.006 | 0.919 ± 0.006 | 0.857 ± 0.013 |
| Reactions per amplifier reshare (default 0.15) | 0.5 | 0.933 ± 0.011 | 0.900 ± 0.012 | 0.939 ± 0.010 |
| Activity skew of users (default 0.7) | 0.5 | 0.956 ± 0.006 | 0.926 ± 0.008 | 0.901 ± 0.009 |
| Activity skew of users (default 0.7) | 0.9 | 0.948 ± 0.008 | 0.913 ± 0.012 | 0.925 ± 0.010 |

## Feature importances (mean over seeds, top 8)

- **share / naive / π = 10% / all:** reuse_overlap_top5 (0.19), t10_s (0.15), delay_ratio_deep_vs_d1 (0.09), reuse_overlap_max (0.07), reuse_shared_top5 (0.05), reuse_shared_max (0.04), median_delay_s (0.04), interarrival_entropy (0.03)
- **share / naive / π = 10% / structure + timing:** t10_s (0.23), delay_ratio_deep_vs_d1 (0.15), median_delay_s (0.06), interarrival_entropy (0.05), offspring_cv (0.03), root_share (0.03), endogenous_share (0.03), depth1_share (0.03)
- **share / naive / π = 30% / all:** reuse_overlap_top5 (0.30), reuse_overlap_max (0.23), median_delay_s (0.09), reuse_shared_top5 (0.08), t10_s (0.06), reuse_shared_max (0.06), delay_ratio_deep_vs_d1 (0.04), offspring_cv (0.02)
- **share / naive / π = 30% / structure + timing:** median_delay_s (0.22), t10_s (0.15), delay_ratio_deep_vs_d1 (0.13), offspring_cv (0.09), root_dominance (0.06), max_breadth (0.04), interarrival_entropy (0.03), size (0.03)
- **strategy / control: embedded accounts / π = 10% / all:** reuse_overlap_top5 (0.27), reuse_overlap_max (0.12), reuse_shared_top5 (0.07), reuse_shared_max (0.05), wiener_index (0.04), size (0.03), structural_virality (0.03), duration_s (0.02)
- **strategy / control: embedded accounts / π = 10% / structure + timing:** median_delay_s (0.05), delay_ratio_deep_vs_d1 (0.05), interarrival_entropy (0.05), t10_s (0.05), t90_s (0.05), t50_s (0.05), duration_s (0.05), offspring_cv (0.04)
- **strategy / control: embedded accounts / π = 30% / all:** reuse_overlap_top5 (0.39), reuse_overlap_max (0.33), reuse_shared_top5 (0.09), reuse_shared_max (0.07), size (0.01), wiener_index (0.01), structural_virality (0.01), distinct_account_share (0.01)
- **strategy / control: embedded accounts / π = 30% / structure + timing:** delay_ratio_deep_vs_d1 (0.05), median_delay_s (0.05), interarrival_entropy (0.05), t90_s (0.05), t10_s (0.05), t50_s (0.05), offspring_cv (0.04), depth2_share (0.04)
- **strategy / full mimic + rotation / π = 10% / all:** leaf_share (0.07), mean_offspring (0.06), outdeg_gini (0.05), reuse_overlap_top5 (0.04), reuse_overlap_max (0.04), delay_ratio_deep_vs_d1 (0.04), interarrival_entropy (0.04), t90_s (0.03)
- **strategy / full mimic + rotation / π = 10% / structure + timing:** mean_offspring (0.07), leaf_share (0.07), outdeg_gini (0.05), delay_ratio_deep_vs_d1 (0.04), interarrival_entropy (0.04), median_delay_s (0.04), t90_s (0.04), offspring_cv (0.04)
- **strategy / full mimic + rotation / π = 30% / all:** leaf_share (0.18), mean_offspring (0.16), outdeg_gini (0.09), reuse_overlap_top5 (0.05), reuse_overlap_max (0.03), wiener_index (0.03), structural_virality (0.03), depth2_share (0.03)
- **strategy / full mimic + rotation / π = 30% / structure + timing:** leaf_share (0.18), mean_offspring (0.18), outdeg_gini (0.10), wiener_index (0.04), structural_virality (0.04), size (0.03), depth2_share (0.03), offspring_cv (0.03)
- **strategy / naive / π = 10% / all:** reuse_overlap_top5 (0.19), t10_s (0.15), delay_ratio_deep_vs_d1 (0.09), reuse_overlap_max (0.07), reuse_shared_top5 (0.05), reuse_shared_max (0.04), median_delay_s (0.04), interarrival_entropy (0.03)
- **strategy / naive / π = 10% / structure + timing:** t10_s (0.23), delay_ratio_deep_vs_d1 (0.15), median_delay_s (0.06), interarrival_entropy (0.05), offspring_cv (0.03), root_share (0.03), endogenous_share (0.03), depth1_share (0.03)
- **strategy / naive / π = 30% / all:** reuse_overlap_top5 (0.30), reuse_overlap_max (0.23), median_delay_s (0.09), reuse_shared_top5 (0.08), t10_s (0.06), reuse_shared_max (0.06), delay_ratio_deep_vs_d1 (0.04), offspring_cv (0.02)
- **strategy / naive / π = 30% / structure + timing:** median_delay_s (0.22), t10_s (0.15), delay_ratio_deep_vs_d1 (0.13), offspring_cv (0.09), root_dominance (0.06), max_breadth (0.04), interarrival_entropy (0.03), size (0.03)
- **strategy / organic timing / π = 10% / all:** reuse_overlap_top5 (0.25), reuse_overlap_max (0.11), reuse_shared_top5 (0.07), reuse_shared_max (0.06), wiener_index (0.03), size (0.03), offspring_cv (0.03), endogenous_share (0.03)
- **strategy / organic timing / π = 10% / structure + timing:** offspring_cv (0.06), root_dominance (0.05), depth2_share (0.05), root_share (0.05), endogenous_share (0.05), depth1_share (0.05), t10_s (0.04), median_delay_s (0.04)
- **strategy / organic timing / π = 30% / all:** reuse_overlap_top5 (0.34), reuse_overlap_max (0.26), reuse_shared_top5 (0.10), reuse_shared_max (0.07), offspring_cv (0.03), root_dominance (0.03), endogenous_share (0.02), root_share (0.02)
- **strategy / organic timing / π = 30% / structure + timing:** offspring_cv (0.13), root_dominance (0.09), outdeg_gini (0.06), root_share (0.05), endogenous_share (0.05), depth1_share (0.05), max_breadth (0.05), wiener_index (0.04)
- **strategy / organic timing + structure / π = 10% / all:** reuse_overlap_top5 (0.25), reuse_overlap_max (0.11), reuse_shared_top5 (0.07), reuse_shared_max (0.05), leaf_share (0.04), wiener_index (0.03), mean_offspring (0.03), size (0.03)
- **strategy / organic timing + structure / π = 10% / structure + timing:** leaf_share (0.07), mean_offspring (0.07), outdeg_gini (0.05), delay_ratio_deep_vs_d1 (0.04), median_delay_s (0.04), offspring_cv (0.04), interarrival_entropy (0.04), t90_s (0.04)
- **strategy / organic timing + structure / π = 30% / all:** reuse_overlap_top5 (0.33), reuse_overlap_max (0.27), reuse_shared_top5 (0.09), leaf_share (0.07), reuse_shared_max (0.06), mean_offspring (0.06), outdeg_gini (0.03), wiener_index (0.01)
- **strategy / organic timing + structure / π = 30% / structure + timing:** leaf_share (0.18), mean_offspring (0.18), outdeg_gini (0.10), wiener_index (0.04), structural_virality (0.03), size (0.03), depth2_share (0.03), offspring_cv (0.03)
- **strategy / random timing / π = 10% / all:** reuse_overlap_top5 (0.18), t10_s (0.15), delay_ratio_deep_vs_d1 (0.09), reuse_overlap_max (0.07), reuse_shared_top5 (0.05), interarrival_entropy (0.05), reuse_shared_max (0.04), median_delay_s (0.03)
- **strategy / random timing / π = 10% / structure + timing:** t10_s (0.23), delay_ratio_deep_vs_d1 (0.14), interarrival_entropy (0.08), median_delay_s (0.06), offspring_cv (0.03), endogenous_share (0.03), root_share (0.03), depth1_share (0.03)
- **strategy / random timing / π = 30% / all:** reuse_overlap_top5 (0.28), reuse_overlap_max (0.22), interarrival_entropy (0.11), median_delay_s (0.07), reuse_shared_top5 (0.07), t10_s (0.05), reuse_shared_max (0.05), delay_ratio_deep_vs_d1 (0.03)
- **strategy / random timing / π = 30% / structure + timing:** interarrival_entropy (0.27), median_delay_s (0.17), t10_s (0.11), delay_ratio_deep_vs_d1 (0.10), offspring_cv (0.07), root_dominance (0.04), max_breadth (0.03), outdeg_gini (0.02)
