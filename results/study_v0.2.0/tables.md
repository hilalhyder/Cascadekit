## E1. AUROC by amplified share (full cascades)

| π target | π realised | size only | shape | branching | timing | reuse | structure + timing | all | all: recall at 1% FPR |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2% | 3.4% | 0.505 ± 0.038 | 0.552 ± 0.012 | 0.539 ± 0.023 | 0.591 ± 0.024 | 0.609 ± 0.052 | 0.615 ± 0.019 | 0.678 ± 0.028 | 0.03 ± 0.00 |
| 5% | 5.2% | 0.534 ± 0.021 | 0.583 ± 0.026 | 0.566 ± 0.021 | 0.730 ± 0.018 | 0.694 ± 0.040 | 0.747 ± 0.013 | 0.810 ± 0.017 | 0.12 ± 0.03 |
| 10% | 9.4% | 0.534 ± 0.043 | 0.654 ± 0.021 | 0.632 ± 0.020 | 0.893 ± 0.011 | 0.832 ± 0.008 | 0.904 ± 0.015 | 0.941 ± 0.009 | 0.47 ± 0.07 |
| 15% | 14.0% | 0.555 ± 0.025 | 0.722 ± 0.019 | 0.688 ± 0.008 | 0.941 ± 0.011 | 0.914 ± 0.012 | 0.950 ± 0.010 | 0.981 ± 0.002 | 0.66 ± 0.07 |
| 20% | 18.0% | 0.568 ± 0.061 | 0.759 ± 0.017 | 0.745 ± 0.009 | 0.950 ± 0.007 | 0.952 ± 0.012 | 0.964 ± 0.003 | 0.988 ± 0.002 | 0.82 ± 0.05 |
| 30% | 25.8% | 0.615 ± 0.022 | 0.841 ± 0.018 | 0.834 ± 0.019 | 0.963 ± 0.004 | 0.982 ± 0.003 | 0.985 ± 0.002 | 0.998 ± 0.001 | 0.96 ± 0.03 |
| 40% | 32.6% | 0.652 ± 0.033 | 0.900 ± 0.013 | 0.895 ± 0.014 | 0.967 ± 0.003 | 0.992 ± 0.003 | 0.993 ± 0.002 | 0.999 ± 0.000 | 0.98 ± 0.00 |
| 60% | 43.7% | 0.773 ± 0.031 | 0.971 ± 0.007 | 0.964 ± 0.007 | 0.980 ± 0.003 | 0.995 ± 0.001 | 0.998 ± 0.001 | 1.000 ± 0.000 | 0.99 ± 0.00 |

## E2. AUROC by reshares seen

| Features | π | first 5 | first 10 | first 20 | first 50 | first 100 | all |
| --- | --- | --- | --- | --- | --- | --- | --- |
| structure + timing | 5% | 0.754 ± 0.029 | 0.767 ± 0.018 | 0.764 ± 0.011 | 0.762 ± 0.017 | 0.755 ± 0.013 | 0.747 ± 0.013 |
| structure + timing | 10% | 0.847 ± 0.011 | 0.851 ± 0.020 | 0.870 ± 0.010 | 0.884 ± 0.013 | 0.899 ± 0.013 | 0.904 ± 0.015 |
| structure + timing | 20% | 0.939 ± 0.005 | 0.950 ± 0.004 | 0.961 ± 0.004 | 0.961 ± 0.005 | 0.963 ± 0.003 | 0.964 ± 0.003 |
| structure + timing | 40% | 0.965 ± 0.002 | 0.994 ± 0.002 | 0.994 ± 0.002 | 0.994 ± 0.001 | 0.994 ± 0.001 | 0.993 ± 0.002 |
| reuse | 5% | 0.965 ± 0.009 | 0.977 ± 0.008 | 0.933 ± 0.006 | 0.810 ± 0.012 | 0.730 ± 0.032 | 0.694 ± 0.040 |
| reuse | 10% | 0.968 ± 0.009 | 0.991 ± 0.004 | 0.976 ± 0.006 | 0.915 ± 0.010 | 0.877 ± 0.015 | 0.832 ± 0.008 |
| reuse | 20% | 0.969 ± 0.005 | 0.993 ± 0.004 | 0.998 ± 0.001 | 0.986 ± 0.004 | 0.973 ± 0.005 | 0.952 ± 0.012 |
| reuse | 40% | 0.967 ± 0.009 | 0.993 ± 0.003 | 0.999 ± 0.001 | 0.998 ± 0.001 | 0.996 ± 0.001 | 0.992 ± 0.003 |
| all | 5% | 0.989 ± 0.002 | 0.981 ± 0.008 | 0.932 ± 0.007 | 0.865 ± 0.016 | 0.832 ± 0.016 | 0.810 ± 0.017 |
| all | 10% | 0.992 ± 0.002 | 0.993 ± 0.003 | 0.979 ± 0.002 | 0.954 ± 0.007 | 0.949 ± 0.008 | 0.941 ± 0.009 |
| all | 20% | 0.993 ± 0.002 | 0.999 ± 0.000 | 0.998 ± 0.001 | 0.996 ± 0.001 | 0.993 ± 0.001 | 0.988 ± 0.002 |
| all | 40% | 0.994 ± 0.003 | 0.999 ± 0.000 | 1.000 ± 0.000 | 1.000 ± 0.000 | 1.000 ± 0.000 | 0.999 ± 0.000 |

## E3. AUROC by organic mean offspring m

| π | Features | m = 0.5 | m = 0.65 | m = 0.8 | m = 0.9 | m = 0.95 |
| --- | --- | --- | --- | --- | --- | --- |
| 10% | size only | 0.558 ± 0.017 | 0.542 ± 0.028 | 0.534 ± 0.043 | 0.536 ± 0.024 | 0.551 ± 0.034 |
| 10% | structure + timing | 0.791 ± 0.022 | 0.854 ± 0.009 | 0.904 ± 0.015 | 0.930 ± 0.009 | 0.947 ± 0.006 |
| 10% | reuse | 0.886 ± 0.010 | 0.857 ± 0.019 | 0.832 ± 0.008 | 0.816 ± 0.013 | 0.780 ± 0.008 |
| 10% | all | 0.923 ± 0.013 | 0.931 ± 0.007 | 0.941 ± 0.009 | 0.945 ± 0.009 | 0.954 ± 0.005 |
| 30% | size only | 0.650 ± 0.012 | 0.633 ± 0.045 | 0.615 ± 0.022 | 0.573 ± 0.017 | 0.580 ± 0.018 |
| 30% | structure + timing | 0.962 ± 0.008 | 0.978 ± 0.008 | 0.985 ± 0.002 | 0.985 ± 0.004 | 0.990 ± 0.002 |
| 30% | reuse | 0.990 ± 0.003 | 0.989 ± 0.004 | 0.982 ± 0.003 | 0.967 ± 0.005 | 0.951 ± 0.009 |
| 30% | all | 0.999 ± 0.000 | 0.999 ± 0.000 | 0.998 ± 0.001 | 0.996 ± 0.002 | 0.996 ± 0.001 |

## E4. Evasion strategies (full cascades)

| π | Strategy | Size only | Structure + timing | Reuse | All | All: recall at 1% FPR | All, trained on naive only |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 10% | naive | 0.534 ± 0.043 | 0.904 ± 0.015 | 0.832 ± 0.008 | 0.941 ± 0.009 | 0.47 ± 0.07 | 0.942 ± 0.008 |
| 10% | random timing | 0.534 ± 0.043 | 0.904 ± 0.015 | 0.832 ± 0.008 | 0.942 ± 0.009 | 0.47 ± 0.07 | 0.943 ± 0.008 |
| 10% | organic timing | 0.538 ± 0.020 | 0.670 ± 0.023 | 0.838 ± 0.019 | 0.871 ± 0.009 | 0.21 ± 0.08 | 0.748 ± 0.020 |
| 10% | organic timing + structure | 0.549 ± 0.019 | 0.660 ± 0.011 | 0.833 ± 0.012 | 0.855 ± 0.009 | 0.21 ± 0.04 | 0.660 ± 0.019 |
| 10% | full mimic + rotation | 0.527 ± 0.029 | 0.641 ± 0.021 | 0.540 ± 0.015 | 0.653 ± 0.019 | 0.04 ± 0.03 | 0.437 ± 0.027 |
| 10% | control: embedded accounts | 0.514 ± 0.032 | 0.499 ± 0.030 | 0.837 ± 0.017 | 0.843 ± 0.009 | 0.12 ± 0.03 | 0.689 ± 0.029 |
| 30% | naive | 0.615 ± 0.022 | 0.985 ± 0.002 | 0.982 ± 0.003 | 0.998 ± 0.001 | 0.96 ± 0.03 | 0.998 ± 0.000 |
| 30% | random timing | 0.615 ± 0.022 | 0.991 ± 0.001 | 0.982 ± 0.003 | 0.998 ± 0.001 | 0.97 ± 0.02 | 0.998 ± 0.000 |
| 30% | organic timing | 0.612 ± 0.040 | 0.855 ± 0.013 | 0.984 ± 0.004 | 0.990 ± 0.002 | 0.89 ± 0.05 | 0.980 ± 0.008 |
| 30% | organic timing + structure | 0.612 ± 0.050 | 0.891 ± 0.011 | 0.980 ± 0.003 | 0.995 ± 0.001 | 0.90 ± 0.04 | 0.951 ± 0.004 |
| 30% | full mimic + rotation | 0.620 ± 0.041 | 0.896 ± 0.012 | 0.723 ± 0.017 | 0.912 ± 0.010 | 0.44 ± 0.12 | 0.492 ± 0.042 |
| 30% | control: embedded accounts | 0.485 ± 0.062 | 0.517 ± 0.039 | 0.989 ± 0.004 | 0.992 ± 0.002 | 0.78 ± 0.04 | 0.969 ± 0.006 |

First 20 reshares only:

| π | Strategy | Structure + timing | Reuse | All |
| --- | --- | --- | --- | --- |
| 10% | naive | 0.870 ± 0.010 | 0.976 ± 0.006 | 0.979 ± 0.002 |
| 10% | random timing | 0.881 ± 0.009 | 0.975 ± 0.006 | 0.979 ± 0.002 |
| 10% | organic timing | 0.661 ± 0.028 | 0.915 ± 0.017 | 0.921 ± 0.011 |
| 10% | organic timing + structure | 0.545 ± 0.011 | 0.647 ± 0.056 | 0.668 ± 0.041 |
| 10% | full mimic + rotation | 0.539 ± 0.038 | 0.512 ± 0.022 | 0.538 ± 0.026 |
| 10% | control: embedded accounts | 0.486 ± 0.025 | 0.741 ± 0.017 | 0.749 ± 0.016 |
| 30% | naive | 0.984 ± 0.003 | 0.999 ± 0.001 | 1.000 ± 0.000 |
| 30% | random timing | 0.989 ± 0.002 | 0.999 ± 0.001 | 1.000 ± 0.000 |
| 30% | organic timing | 0.809 ± 0.012 | 0.983 ± 0.003 | 0.996 ± 0.002 |
| 30% | organic timing + structure | 0.699 ± 0.028 | 0.802 ± 0.020 | 0.869 ± 0.018 |
| 30% | full mimic + rotation | 0.708 ± 0.025 | 0.582 ± 0.019 | 0.721 ± 0.025 |
| 30% | control: embedded accounts | 0.517 ± 0.018 | 0.923 ± 0.009 | 0.932 ± 0.010 |

## E4. What each strategy costs the attacker

| π | Strategy | Minutes until 90% of amplifier reshares land | Amplifier reshares in first hour | Accounts used per campaign | Cascades per account | Reshares in first hour, amplified | Reshares in first hour, organic |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 10% | naive | 7 | 100% | 41 | 7.5 | 23.5 | 14.1 |
| 10% | random timing | 7 | 100% | 41 | 7.5 | 23.5 | 14.1 |
| 10% | organic timing | 124 | 67% | 40 | 7.7 | 20.2 | 14.1 |
| 10% | organic timing + structure | 449 | 16% | 38 | 7.9 | 15.2 | 14.1 |
| 10% | full mimic + rotation | 457 | 16% | 287 | 1.0 | 14.8 | 14.1 |
| 10% | control: embedded accounts | 319 | 31% | 33 | 7.9 | 13.9 | 14.1 |
| 30% | naive | 11 | 100% | 130 | 8.5 | 45.5 | 14.1 |
| 30% | random timing | 11 | 100% | 130 | 8.5 | 45.5 | 14.1 |
| 30% | organic timing | 177 | 63% | 125 | 8.9 | 33.4 | 14.1 |
| 30% | organic timing + structure | 548 | 14% | 124 | 9.1 | 17.3 | 14.1 |
| 30% | full mimic + rotation | 539 | 15% | 1027 | 1.1 | 17.2 | 14.1 |
| 30% | control: embedded accounts | 408 | 30% | 102 | 8.1 | 15.0 | 14.1 |

## E4b. Account rotation under the full-mimic strategy (π = 20%)

| Pool size per campaign | Accounts actually used | Cascades per account | Reuse AUROC | All AUROC |
| --- | --- | --- | --- | --- |
| 50 | 50 | 11.74 | 0.965 ± 0.010 | 0.974 ± 0.003 |
| 150 | 148 | 4.43 | 0.736 ± 0.017 | 0.850 ± 0.029 |
| 500 | 378 | 1.81 | 0.659 ± 0.020 | 0.819 ± 0.025 |
| 2,000 | 588 | 1.18 | 0.651 ± 0.027 | 0.821 ± 0.020 |
| 10,000 | 650 | 1.03 | 0.644 ± 0.021 | 0.828 ± 0.016 |

## E4c. Late start of a naive campaign (π = 20%)

| Start delay | View | Structure + timing | Reuse | All |
| --- | --- | --- | --- | --- |
| 5 min | first 20 | 0.961 ± 0.004 | 0.998 ± 0.001 | 0.998 ± 0.001 |
| 5 min | all | 0.964 ± 0.003 | 0.952 ± 0.012 | 0.988 ± 0.002 |
| 60 min | first 20 | 0.825 ± 0.006 | 0.869 ± 0.020 | 0.925 ± 0.005 |
| 60 min | all | 0.909 ± 0.008 | 0.952 ± 0.012 | 0.980 ± 0.003 |
| 360 min | first 20 | 0.672 ± 0.016 | 0.670 ± 0.035 | 0.712 ± 0.020 |
| 360 min | all | 0.979 ± 0.002 | 0.952 ± 0.012 | 0.994 ± 0.002 |

## E5. Base rate (π = 10%, 200 amplified cascades)

| Strategy | Amplified share of corpus | Features | AUROC | Average precision | Recall at 1% FPR |
| --- | --- | --- | --- | --- | --- |
| naive | 50% | structure + timing | 0.901 ± 0.020 | 0.898 ± 0.024 | 0.32 ± 0.12 |
| naive | 50% | reuse | 0.858 ± 0.016 | 0.824 ± 0.020 | 0.10 ± 0.05 |
| naive | 50% | all | 0.941 ± 0.015 | 0.937 ± 0.015 | 0.47 ± 0.01 |
| naive | 10% | structure + timing | 0.902 ± 0.003 | 0.636 ± 0.039 | 0.38 ± 0.08 |
| naive | 10% | reuse | 0.698 ± 0.044 | 0.200 ± 0.052 | 0.03 ± 0.02 |
| naive | 10% | all | 0.921 ± 0.003 | 0.697 ± 0.048 | 0.44 ± 0.05 |
| naive | 2% | structure + timing | 0.875 ± 0.009 | 0.437 ± 0.041 | 0.44 ± 0.03 |
| naive | 2% | reuse | 0.547 ± 0.022 | 0.025 ± 0.003 | 0.02 ± 0.01 |
| naive | 2% | all | 0.889 ± 0.004 | 0.454 ± 0.041 | 0.44 ± 0.02 |
| organic timing + structure | 50% | structure + timing | 0.641 ± 0.019 | 0.627 ± 0.028 | 0.02 ± 0.00 |
| organic timing + structure | 50% | reuse | 0.850 ± 0.005 | 0.828 ± 0.025 | 0.12 ± 0.06 |
| organic timing + structure | 50% | all | 0.854 ± 0.008 | 0.838 ± 0.007 | 0.16 ± 0.05 |
| organic timing + structure | 10% | structure + timing | 0.627 ± 0.009 | 0.180 ± 0.012 | 0.05 ± 0.01 |
| organic timing + structure | 10% | reuse | 0.743 ± 0.029 | 0.246 ± 0.033 | 0.06 ± 0.01 |
| organic timing + structure | 10% | all | 0.773 ± 0.013 | 0.340 ± 0.016 | 0.14 ± 0.01 |
| organic timing + structure | 2% | structure + timing | 0.617 ± 0.013 | 0.044 ± 0.005 | 0.05 ± 0.01 |
| organic timing + structure | 2% | reuse | 0.590 ± 0.006 | 0.027 ± 0.003 | 0.01 ± 0.01 |
| organic timing + structure | 2% | all | 0.650 ± 0.024 | 0.052 ± 0.009 | 0.06 ± 0.01 |

## Feature importances (mean over seeds, top 8)

- **share / naive / π = 10% / all:** t10_s (0.19), reuse_share_5plus (0.16), delay_ratio_deep_vs_d1 (0.11), reuse_mean (0.06), median_delay_s (0.05), interarrival_entropy (0.04), offspring_cv (0.03), depth1_share (0.02)
- **share / naive / π = 10% / structure + timing:** t10_s (0.24), delay_ratio_deep_vs_d1 (0.13), median_delay_s (0.06), interarrival_entropy (0.05), offspring_cv (0.04), root_share (0.03), endogenous_share (0.03), depth1_share (0.03)
- **share / naive / π = 30% / all:** reuse_share_5plus (0.30), median_delay_s (0.14), t10_s (0.09), delay_ratio_deep_vs_d1 (0.08), offspring_cv (0.06), reuse_mean (0.06), root_dominance (0.05), max_breadth (0.03)
- **share / naive / π = 30% / structure + timing:** median_delay_s (0.22), t10_s (0.15), delay_ratio_deep_vs_d1 (0.13), offspring_cv (0.10), root_dominance (0.06), max_breadth (0.04), interarrival_entropy (0.04), outdeg_gini (0.03)
- **strategy / control: embedded accounts / π = 10% / all:** reuse_share_5plus (0.28), reuse_mean (0.10), wiener_index (0.03), median_delay_s (0.03), duration_s (0.03), interarrival_entropy (0.03), t90_s (0.03), offspring_cv (0.03)
- **strategy / control: embedded accounts / π = 10% / structure + timing:** median_delay_s (0.05), delay_ratio_deep_vs_d1 (0.05), interarrival_entropy (0.05), t10_s (0.05), t90_s (0.05), t50_s (0.05), duration_s (0.05), depth2_share (0.04)
- **strategy / control: embedded accounts / π = 30% / all:** reuse_share_5plus (0.53), reuse_mean (0.22), wiener_index (0.02), size (0.01), distinct_account_share (0.01), structural_virality (0.01), median_delay_s (0.01), t50_s (0.01)
- **strategy / control: embedded accounts / π = 30% / structure + timing:** delay_ratio_deep_vs_d1 (0.05), median_delay_s (0.05), interarrival_entropy (0.05), t90_s (0.05), t50_s (0.05), t10_s (0.05), offspring_cv (0.04), depth2_share (0.04)
- **strategy / full mimic + rotation / π = 10% / all:** leaf_share (0.07), mean_offspring (0.06), outdeg_gini (0.05), reuse_share_5plus (0.05), reuse_mean (0.04), delay_ratio_deep_vs_d1 (0.04), median_delay_s (0.04), offspring_cv (0.04)
- **strategy / full mimic + rotation / π = 10% / structure + timing:** leaf_share (0.07), mean_offspring (0.07), outdeg_gini (0.05), delay_ratio_deep_vs_d1 (0.04), median_delay_s (0.04), offspring_cv (0.04), depth2_share (0.04), interarrival_entropy (0.04)
- **strategy / full mimic + rotation / π = 30% / all:** leaf_share (0.17), mean_offspring (0.14), outdeg_gini (0.09), reuse_share_5plus (0.09), reuse_mean (0.04), wiener_index (0.03), structural_virality (0.03), size (0.03)
- **strategy / full mimic + rotation / π = 30% / structure + timing:** leaf_share (0.18), mean_offspring (0.16), outdeg_gini (0.10), wiener_index (0.04), structural_virality (0.04), size (0.03), depth2_share (0.03), offspring_cv (0.03)
- **strategy / naive / π = 10% / all:** t10_s (0.19), reuse_share_5plus (0.16), delay_ratio_deep_vs_d1 (0.11), reuse_mean (0.06), median_delay_s (0.05), interarrival_entropy (0.04), offspring_cv (0.03), depth1_share (0.02)
- **strategy / naive / π = 10% / structure + timing:** t10_s (0.24), delay_ratio_deep_vs_d1 (0.13), median_delay_s (0.06), interarrival_entropy (0.05), offspring_cv (0.04), root_share (0.03), endogenous_share (0.03), depth1_share (0.03)
- **strategy / naive / π = 30% / all:** reuse_share_5plus (0.30), median_delay_s (0.14), t10_s (0.09), delay_ratio_deep_vs_d1 (0.08), offspring_cv (0.06), reuse_mean (0.06), root_dominance (0.05), max_breadth (0.03)
- **strategy / naive / π = 30% / structure + timing:** median_delay_s (0.22), t10_s (0.15), delay_ratio_deep_vs_d1 (0.13), offspring_cv (0.10), root_dominance (0.06), max_breadth (0.04), interarrival_entropy (0.04), outdeg_gini (0.03)
- **strategy / organic timing / π = 10% / all:** reuse_share_5plus (0.25), reuse_mean (0.08), offspring_cv (0.04), root_dominance (0.04), depth1_share (0.04), root_share (0.03), endogenous_share (0.03), depth2_share (0.03)
- **strategy / organic timing / π = 10% / structure + timing:** offspring_cv (0.06), root_dominance (0.05), depth2_share (0.05), endogenous_share (0.05), root_share (0.05), depth1_share (0.05), t10_s (0.04), median_delay_s (0.04)
- **strategy / organic timing / π = 30% / all:** reuse_share_5plus (0.39), reuse_mean (0.11), offspring_cv (0.09), root_dominance (0.06), outdeg_gini (0.04), max_breadth (0.03), depth1_share (0.03), endogenous_share (0.03)
- **strategy / organic timing / π = 30% / structure + timing:** offspring_cv (0.14), root_dominance (0.09), outdeg_gini (0.06), endogenous_share (0.05), root_share (0.05), depth1_share (0.05), max_breadth (0.05), wiener_index (0.04)
- **strategy / organic timing + structure / π = 10% / all:** reuse_share_5plus (0.25), reuse_mean (0.08), leaf_share (0.05), mean_offspring (0.05), outdeg_gini (0.03), wiener_index (0.03), offspring_cv (0.03), median_delay_s (0.03)
- **strategy / organic timing + structure / π = 10% / structure + timing:** leaf_share (0.07), mean_offspring (0.07), outdeg_gini (0.05), offspring_cv (0.04), delay_ratio_deep_vs_d1 (0.04), median_delay_s (0.04), t90_s (0.04), t10_s (0.04)
- **strategy / organic timing + structure / π = 30% / all:** reuse_share_5plus (0.39), leaf_share (0.11), reuse_mean (0.11), mean_offspring (0.08), outdeg_gini (0.05), wiener_index (0.02), size (0.02), structural_virality (0.02)
- **strategy / organic timing + structure / π = 30% / structure + timing:** leaf_share (0.18), mean_offspring (0.16), outdeg_gini (0.09), wiener_index (0.04), structural_virality (0.04), size (0.03), depth2_share (0.03), offspring_cv (0.03)
- **strategy / random timing / π = 10% / all:** t10_s (0.19), reuse_share_5plus (0.16), delay_ratio_deep_vs_d1 (0.10), interarrival_entropy (0.06), reuse_mean (0.06), median_delay_s (0.04), offspring_cv (0.02), root_share (0.02)
- **strategy / random timing / π = 10% / structure + timing:** t10_s (0.23), delay_ratio_deep_vs_d1 (0.13), interarrival_entropy (0.08), median_delay_s (0.06), offspring_cv (0.03), endogenous_share (0.03), root_share (0.03), wiener_index (0.03)
- **strategy / random timing / π = 30% / all:** reuse_share_5plus (0.27), interarrival_entropy (0.17), median_delay_s (0.12), t10_s (0.07), delay_ratio_deep_vs_d1 (0.06), offspring_cv (0.05), reuse_mean (0.05), root_dominance (0.04)
- **strategy / random timing / π = 30% / structure + timing:** interarrival_entropy (0.28), median_delay_s (0.16), t10_s (0.11), delay_ratio_deep_vs_d1 (0.09), offspring_cv (0.07), root_dominance (0.04), max_breadth (0.03), outdeg_gini (0.02)
