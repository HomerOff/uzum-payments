from setuptools import setup, find_packages

with open('README.md', encoding='utf8') as f:
    long_description = f.read()

setup(
    name='uzum-payments',
    version='0.0.2',
    author='Vsevolod Slivсa',
    description='Uzum Payments API Client',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT',
    url='https://github.com/homeroff/uzum-payments/',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Office/Business',
        'Topic :: Office/Business :: Financial',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    python_requires='>=3.6',
    project_urls={
        'Source Code': 'https://github.com/homeroff/uzum-payments/',
        'Issue Tracker': 'https://github.com/homeroff/uzum-payments/issues',
        'Documentation': 'https://www.inplat-tech.ru/docs/checkout/'
    },
    install_requires=['requests'], 
)