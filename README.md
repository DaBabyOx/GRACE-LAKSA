# GRACE-LAKSA Public Verification Bundle

Public verification artifacts for:

> **GRACE-LAKSA: A Retrieval-Augmented Graph Framework for Long-Tail Civic Complaint Understanding and Routing**

This repository contains verification code and aggregate experimental results used to check the arithmetic and summary claims reported in the paper.

**No complaint-level data are included.**

## Verification

The public verification suite requires only the Python standard library:

```bash
python verify.py
```

The verifier checks:

* reconstruction of the reported main score:

  ```text
  0.45 * category_macro_f1
  + 0.30 * category_tail_f1
  + 0.25 * opd_macro_f1
  ```

* clean-versus-leaky evaluation deltas;

* rolling-CV significance fields;

* consistency of released aggregate results;

* the public-release file allowlist; and

* privacy-sensitive column names.

Maintainers with access to the private research repository can additionally verify that the published aggregates correspond to the recorded source artifacts:

```bash
python verify.py --private-root ..
```

## Data and Privacy

The original Tangerang City complaint data are subject to municipal data-sharing and privacy restrictions and are **not distributed with this repository**.

The public bundle intentionally excludes:

* complaint text, identifiers, timestamps, labels, and locations;
* train/validation/test membership;
* per-complaint predictions;
* embeddings and retrieval indices;
* model weights and checkpoints; and
* credentials and notification configuration.

The software license for this repository does **not** grant rights to the original municipal dataset.

## Scope of Verification

Passing the public verification suite confirms the **internal consistency of the released aggregate results and supported summary calculations**.

It does **not** reproduce model training or independently reconstruct the reported experiments from complaint-level observations because the underlying municipal complaint records cannot be publicly released.

The synthetic retrieval-latency table and the later paired holdout randomization test are currently excluded from the verifier because neither has a durable source artifact under `outputs/`.

## Paper

The accompanying paper evaluates GRACE-LAKSA on 13,618 Tangerang City complaints spanning 301 complaint categories and 131 government-agency routing labels.

The public repository is intended to provide a transparent, privacy-preserving verification layer for the quantitative claims that can be checked without releasing restricted complaint-level information.

## Citation

If you use this verification bundle or build upon the GRACE-LAKSA work, please cite:

```bibtex
@inproceedings{tarigan2026gracelaksa,
  title     = {GRACE-LAKSA: A Retrieval-Augmented Graph Framework for Long-Tail Civic Complaint Understanding and Routing},
  author    = {Tarigan, Daffa Farras Putra and
               Fransisco, Kevin and
               Swastika, Arya and
               Madyatmadja, Evaristus Didik},
  booktitle = {IEEE FMLDS},
  year      = {2026}
}
```

Final publication metadata should be used once the IEEE proceedings are available.

## License

The verification software in this repository is released under the **Apache License 2.0**.

The license applies only to the software and other explicitly released repository artifacts. It does not apply to the original Tangerang City complaint dataset, which is not distributed here.

Third-party software and resources remain subject to their respective licenses.

## Authors

Daffa Farras Putra Tarigan
Kevin Fransisco
Arya Swastika
Evaristus Didik Madyatmadja

School of Information Systems
Bina Nusantara University
