# Hypergammy — Multi-Reference Facial Geometry Analysis

> An experimental computer-vision system designed to compare facial measurements against a user-defined reference profile using a 34-image reference set for each facial feature.

## Project purpose
Hypergammy treats facial geometry as a measurable image-analysis problem. A face image is processed to extract landmarks and geometric measurements, then measurements for each facial region are compared mathematically with a corresponding reference collection. The design uses **34 reference images per feature/region**, rather than depending on one single reference image.

The “perfect” face in this project means a target profile defined by the selected reference measurements. It is not an objective or universal definition of beauty, and the output is not a medical, psychological, identity, or scientific attractiveness assessment.

## Intended pipeline
1. Upload a face image.
2. Detect the face and locate facial landmarks.
3. Derive normalized geometric measurements for relevant facial regions.
4. Compare each feature's measurements against its 34-image reference set.
5. Calculate numerical distances/similarity values relative to the chosen target profile.
6. Present a breakdown showing which measured regions are closer to or farther from the reference.

## Why multiple references?
A set of references can reduce dependence on the proportions, lighting, pose, and perspective of a single image. It does not eliminate dataset bias or measurement error. The reliability of comparisons depends on consistent image capture, landmark quality, normalization, reference selection, and the mathematical scoring rules.

## Current repository packaging
The repository currently exposes the project as a ZIP archive, `haypergammy (2).zip`, alongside this README. The source files and exact run manifests are not expanded at the repository root. Download/clone the repository and extract the ZIP into a separate working directory:
```bash
git clone https://github.com/aloslsaid/hypergammy.git
cd hypergammy
```
Then extract `haypergammy (2).zip` and follow the package-specific instructions inside the extracted project. Since the root does not expose its `package.json`, `requirements.txt`, or entry point, this README does not invent a launch command.

## Responsible use
Facial images and derived measurements are sensitive biometric information. Use images only with permission, protect stored files, and avoid making decisions about people based on a similarity score. Lighting, pose, expression, age, camera optics, and individual variation can change measurements. The output represents this project's reference model—not a ranking of human value.

## Concepts demonstrated
Computer vision · Facial landmarks · Geometric feature extraction · Reference-set comparison · Numerical similarity · Image normalization · Experimental scoring
