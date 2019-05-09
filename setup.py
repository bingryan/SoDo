from setuptools import setup, find_packages

setup(
    name='SoDo',
    version='1.0.0',
    description=(
        'Redis-based  scheduler and Message queue Spider for Scrapy,  '
        'Provide more flexible and practical ways for Scrapy'),
    long_description=open('README.md').read(),
    packages=find_packages(exclude=('tests', 'tests.*')),
    include_package_data=True,
    url='https://github.com/ycvbcvfu/sodo',
    license='MIT License',
    author='ryan',
    maintainer='ryan',
    author_email='legotime@qq.com',
    install_requires=[
        'Scrapy',
        'kafka',
        'redis'
    ]
)
