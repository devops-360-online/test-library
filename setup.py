from setuptools import setup, find_packages

with open('simple_observability/requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name="simple_observability",
    version="0.1.0",
    description="Auto-instrumentation library for metrics, logs and traces with a single line of code",
    author="Your Organization",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries",
        "Topic :: System :: Monitoring",
    ],
    python_requires=">=3.8",
) 