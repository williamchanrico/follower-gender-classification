# svm

Implementation of support vector machine algorithm to classify gender,
based on comments from instagram media(s).

## Setup

Assuming you have `virtualenv` installed:

- `virtualenv venv && source venv/bin/activate`
- `pip install -r requirements.txt`
- `python3 svm.py --help`

```
$ ./svm.py -h
usage: svm.py [-h] [-l LIMIT] [-e LIMIT_PER_GENDER] [-c] [-g GAMMA]
              [-k KERNEL]

optional arguments:
  -h, --help            show this help message and exit
  -l LIMIT, --limit LIMIT
                        Limit processed data, equal male and female comments
  -e LIMIT_PER_GENDER, --limit-per-gender LIMIT_PER_GENDER
                        Limit per gender
  -c, --cache           Cache processed raw data
  -g GAMMA, --gamma GAMMA
                        Kernel coefficient for ‘rbf’, ‘poly’ and ‘sigmoid’
  -k KERNEL, --kernel KERNEL
                        Specifies the kernel type to be used in the algorithm
```

- `deactivate`

## Words Blacklist

Put blacklisted words in `data/blacklist.txt` (one word per line)

They will be read at the beginning of the program.

## Example

```
$ ./svm.py --limit 1000 --kernel rbf
Running SVM Classifier
Reading blacklist words file
Reading raw gender-comment data
Loaded 23499 male and 51030 female comments
Limiting male and female comments to 500 each (1000 total)
Total of 3050 words found
Processing 1000 raw gender-comment data: [########################################]

Running tests
=============
Kernel: rbf
Gamma: 1
=============

Test-1
> Training model...
> Predicting test data...
> Accuracy: 52.00%

Test-2
> Training model...
> Predicting test data...
> Accuracy: 52.00%

Test-3
> Training model...
> Predicting test data...
> Accuracy: 52.80%

Test-4
> Training model...
> Predicting test data...
> Accuracy: 45.60%

Test-5
> Training model...
> Predicting test data...
> Accuracy: 58.40%

Test-6
> Training model...
> Predicting test data...
> Accuracy: 57.60%

Test-7
> Training model...
> Predicting test data...
> Accuracy: 50.40%

Test-8
> Training model...
> Predicting test data...
> Accuracy: 49.60%

=====================================
Avg. Accuracy: 52.30%
Elapsed time: 62.53s
```

## Reference

`https://scikit-learn.org/stable/modules/svm.html`