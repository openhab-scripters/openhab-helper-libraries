This change log will keep track of what has been done in the `ivans-updates` branch.

# Python

## Added

* Custom logger class and simplier `getLogger` function that automatically prepends the `LOG_PREFIX`.
* OH3.x support while maintaining backwards compatibility with OH2.x.

## Changed

* `when` and `addRule` now use `scriptExtension` instead of `scope`, see [commit](https://github.com/CrazyIvan359/openhab-helper-libraries/commit/cbc5e01b65cb614cced80e482b74dae523aed75f) for details.
* Some core logging changed from `DEBUG` TO `TRACE`.

## Fixed

* Generic Event triggers (Item/Thing added/removed/modified, Thing Status, etc) will now work in OH2.x and OH3.x.

# Javascript

## Added

## Changed

## Fixed
