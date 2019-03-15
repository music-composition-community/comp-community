from setuptools import setup, find_packages


setup(
    name="comp-community-scripts",
    version="1.0.1",
    description="Scripts for working with comp-community",
    author="Nick Florin",
    author_email="nickmflorin@gmamil.com",
    url="https://github.com/music-composition-community/comp-community",
    packages=find_packages(),
    install_requires=[
        'plumbum',
        'six',
        'tornado==4.4.2',
        'psutil',
        'docker-compose==1.16.1',
        'docker==2.5.1',
        'requests==2.11.1',
    ],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'comp = comp_community_scripts.__main__:main',
        ],
    },
    zip_safe=False)
