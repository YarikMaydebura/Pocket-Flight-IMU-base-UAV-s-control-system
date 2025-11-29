# Contributing to PocketFlight

Thank you for your interest in contributing to PocketFlight! This document provides guidelines for contributing to the project.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue on GitHub with:
- A clear, descriptive title
- Steps to reproduce the issue
- Expected behavior vs actual behavior
- Your environment (OS, ROS version, Python version)
- Screenshots or logs if applicable

### Suggesting Enhancements

Feature suggestions are welcome! Please create an issue with:
- A clear description of the feature
- Why this feature would be useful
- Potential implementation approach (if you have one)

### Pull Requests

1. **Fork the repository**
   ```bash
   git clone https://github.com/YourUsername/PocketFlight.git
   cd PocketFlight
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow the existing code style
   - Add comments for complex logic
   - Update documentation if needed

4. **Test your changes**
   - Ensure the code runs without errors
   - Test in Gazebo simulation
   - Verify with real hardware if possible

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add feature: description of your changes"
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request**
   - Go to the original repository on GitHub
   - Click "New Pull Request"
   - Select your feature branch
   - Provide a clear description of your changes

## Code Style Guidelines

### Python
- Follow PEP 8 style guide
- Use meaningful variable names
- Add docstrings to functions
- Keep functions focused and concise

Example:
```python
def calculate_velocity(imu_data, scaling_factor):
    """
    Calculate drone velocity from IMU data.

    Args:
        imu_data (dict): IMU sensor readings
        scaling_factor (float): Velocity scaling factor

    Returns:
        float: Calculated velocity
    """
    return imu_data['acceleration'] * scaling_factor
```

### ROS Nodes
- Use clear, descriptive topic names
- Add rospy.loginfo() for important events
- Handle exceptions gracefully
- Clean up resources in shutdown handlers

### Launch Files
- Add comments explaining parameters
- Use descriptive node names
- Group related nodes together

## Areas for Contribution

We welcome contributions in these areas:

- **Documentation**: Improve installation guides, add tutorials
- **Testing**: Add unit tests, integration tests
- **Features**:
  - Multi-drone coordination
  - Improved flood detection algorithms
  - Real hardware support (DJI Tello, etc.)
  - Haptic feedback integration
- **Performance**: Optimize control loops, reduce latency
- **UI/UX**: Create ground control station interface

## Questions?

If you have questions about contributing, feel free to:
- Open an issue on GitHub
- Contact the maintainers

## License

By contributing to PocketFlight, you agree that your contributions will be licensed under the GPL-3.0 License.
