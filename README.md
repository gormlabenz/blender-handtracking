# Blender Handtracking

Blender Handtracking is a powerful addon that enables you to control the Blender viewport using hand tracking. This project is in its alpha stage and under heavy development, so please expect changes and improvements over time.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## Installation

1. Clone this repository or download it as a ZIP file.
2. Install the required Python packages:```
   Copy codepip install -r requirements.txt

   ```

   ```

3. Navigate to the repository folder and start the `server.py` script:```
   Copy codepython server.py

   ```

   ```

4. Start the `tracking.py` script in a separate terminal/command prompt:```
   Copy codepython tracking.py

   ```

   ```

5. Open Blender and go to `Edit > Preferences > Add-ons > Install`.
6. Navigate to the repository folder and select the `addon.py` file to install the addon.

## Usage

After installing the addon, make sure the `server.py` and `tracking.py` scripts are running. In Blender, you can enable the addon in the Add-ons panel by checking the box next to "Blender Handtracking".

With the addon enabled, you can now control the Blender viewport using hand tracking. Please note that the addon is still in its alpha stage, so some features may not work perfectly, and there might be some bugs.

## Project Structure

- `addon.py`: This is the Blender addon script that integrates the hand tracking functionality into Blender.
- `tracking.py`: This script handles the hand tracking logic using a dedicated hand tracking library.
- `server.py`: This script connects the `tracking.py` script and the `addon.py` addon via a socket to communicate tracking data.

## Contributing

We welcome contributions to the Blender Handtracking repository! If you find a bug, have an idea for a new feature, or would like to help with development, please follow these steps:

1. Fork the repository.
2. Create a new branch for your changes.
3. Make your changes and commit them to your branch.
4. Create a pull request, describing the changes you've made and why they're important.

Please keep in mind that this project is in its alpha stage, so your contributions can significantly help improve the addon's functionality and stability.

## License

This project is licensed under the [MIT License](LICENSE). Please see the [LICENSE](LICENSE) file for more information.
