# Memorize PreFlop

Memorize Preflop is a simple tool for memorizing preflop ranges. It has a range builder, a chart trainer, hand traininer, and custom reporting system. It allows for users to custom train any set of ranges from both a chart and hand persepective. Intro video: video
![Memorize PreFlop Demo Image](/images/mem1.png "Hand Trainer") ![Memorize PreFlop Demo Image](/images/mem2.png "Chart Trainer") ![Memorize PreFlop Demo Image](/images/mem3.png "Hand Training Report")


# Usage Demo
Please checkout this youtube video for a simple example on how Memorize Preflop can be used!

# Installation
## Windows

<a id="raw-url" href="https://raw.githubusercontent.com/lukebhan/memorizePreFlop/master/MemorizePreflopWindows.zip">Windows</a>

Windows installation is the easiest. Just click the link above and extract the folder. Then to run the application, just click on the file titled Memorize Preflop. 

## MacOS and Linux
Currently, MacOS and Linux binaries are not available (Will be available in early January!). However, it is still very easy to build from source, but one will need a few dependencies: Python, Numpy and PyQT5. A simple list of steps to follow are listed here (Folks familiar with programming can easily just run the sol.py file in src folder if they have dependencies installed):
1. Install python through Anaconda <a href="https://www.anaconda.com/products/distribution"> Anaconda Install </a>
2. Open your terminal in finder. On Mac, press command space bar and search terminal.
3. (Optional) Create a virtual env: ```conda create -n memorizePreflop python=3.8'''
4. Install Dependencies:
  a) ```conda install PyQt```
  b) ```conda install numpy```
5. Download the source. The easiest way is through git: ```git clone https://github.com/lukebhan/memorizePreFlop.git```
6. Navigate to folder. ```cd memorizePreFlop/src```
7. Run the application ```python sol.py```

# Contributing
MemorizePreFlop will always be **Free** and **Open Source**. Feel free to submit a pull request with any ideas or bugs you find. Also, if you don't want to go through solving the bug, feel free to make an issue.

# License
This is licensed under <a href="https://www.gnu.org/licenses/agpl-3.0.en.html> GNU </a>.




