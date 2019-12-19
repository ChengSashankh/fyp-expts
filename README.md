# FYP: Mathematical Equation Understanding

## Repository Contents

This repository contains the following information:

|               What               |                Where               |
|:--------------------------------:|:----------------------------------:|
| Source code for each experiment  |       `expt/experiment-name`       |
|    Results for each experiment   |    `README.md` and GitHub Pages    |
|      Slides at each meeting      |         `slides/slides.pdf`        |
|       Datasets created/used      | Link in README.md and GitHub Pages |
|        Material for report       |              `report/`             |
|        Table Examples here       |              [examples](docs/table-examples.md)             |


## Some relevant literature

The following papers are some relevant to this project.

| Paper Title                                               | Paper Link                                                              | Notes  |
|-----------------------------------------------------------|-------------------------------------------------------------------------| -------|
| Equation Embeddings                                       | [Paper Link](https://arxiv.org/abs/1803.09123)                          | [Notes](docs/paper-notes.md/#equation-embeddings)
| A Comprehensive Review of Graph Convolution Networks      | [Paper Link](https://arxiv.org/pdf/1901.00596.pdf)                      | [Notes](docs/paper-notes.md/#gcn-comprehensive-review)
| Tangent-CFT: An Embedding Model for Mathematical Formulas | [Paper Link](https://www.cs.rit.edu/~rlaz/files/Mansouri_ICTIR2019.pdf) | [Notes](docs/paper-notes.md/#tangent-ctf-mathematical-formula-embedding)


## Vacation Progress Journal

- Task Status is shown on the project board [`Task Board`](https://github.com/ChengSashankh/fyp-expts/projects/1).
- List of currently active issues are listed [here](https://github.com/ChengSashankh/fyp-expts/issues).


For quick reference, the status is also documented here:

|   | Start Date | End Date | Issue |                                                   Task Title                                                   |                                                                                                                       Description                                                                                                                       |         Status        |
|:-:|:----------:|:--------:|:-----:|:--------------------------------------------------------------------------------------------------------------:|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|:---------------------:|
| 1 |   Dec 11   |  Dec 12  |   #8  |                                             Admin (Re-organization)                                            |                                                                    Collecting work in one repo, documenting current progress neatly, establishing straightforward experiment process.                                                                   | Done [Recurring task] |
| 2 |   Dec 12   |  Dec 13  |   #7  |                                           Understanding GCN Examples                                           |                                                                            Reading some basic literature about GCN Networks, and how to adapt existing GCN code for this task                                                                           |         In Progress         |
| 3 |   Dec 13   |  Dec 13  |   #1  |                               Re-run seq2seq model to obtain reasonable insights                               |                                                                                        Run seq2seq locally with better linguistic preprocessing and distribution.                                                                                       |         Running        |
| 4 |   Dec 14   |  Dec 15  |   #3  |                                          Modelling Current Task as GCN                                         |                                                                                    (After #7) Design GCN for equation task, and create data set, document impediments                                                                                   |         To do         |
| 5 |   Dec 16   |  Dec 17  |  #11  |                               Consolidate Results From Sequence and Graph Models                               |             After effort on modelling as GCN and fixing seq2seq models, there is expected to be some troubleshooting/re-evaluation of approach required in order to obtain meaningful results. This issue will schedule time for such tasks.            |         Partially In Progress         |
| 6 |   Dec 18   |  Dec 20  |   #2  | Identify Different Labelled Task to Evaluate Embeddings Attempt a BERT based approach as a secondary baseline. | - Use the metadata provided along with the papers to create labelled task. This will be the target task. - Use SciBERT + sequence method for equation to generate joint embeddings. - Use these embeddings for the labelled task and report performance |         To do         |
| 7 |   Dec 19   |  Dec 19  |   #5  |                                           Extract Tables from Papers                                           |                                                                                                     Extract tables from papers for side experiments.                                                                                                    |         Done        |
| 8 |   Dec 21   |  Dec 23  |   -   |                                        Buffer Days / Other commitments                                         |                                                                                                             Buffer Days / Other commitments                                                                                                             |           -           |
