# peak_picker
The "peak_picker" code allows you to pick a certain peak of a response, for example wave V of the ABR, and obtain the latency and amplitude of that peak. This is done for all conditions for that subject, and can be done for as many subjects in a loop. The data is saved as a figure, hdf5 file and text file (but you can choose which files to save in the "user settings" chunk of code).

To run: The code can be run from a console or terminal. I found that it runs best from the terminal using python3: python -i peak_picker.py

An interactive figure is given for each subject (ie can pan in/out etc). After picking peaks, close the figure. Then in the console or terminal, press Enter to bring up the next figure.

The data are saved as a dictionary with latency and amplitude, each themselves as dictionaries with a label for each response. The labels are set in line 177.

To pick a peak: For each waveform, 2 points need to be "picked" to give the amplitude - the peak and then some later point on the waveform. For example, pick wave V peak latency (and a + will show up on the waveform) and then at the following negative trough (another + will show up). Once both points on the response are chosen, the line becomes thicker, making it easier to know which responses have been fully marked. Responses without markings are given "NaN" (or amplitudes are "NaN" if there weren't 2 points chosen on the response, to calculate the difference in amplitude between the two points).

An example of an incomplete set of markings:
![mjp_pABRrates_000_V](https://user-images.githubusercontent.com/15331606/113761344-56a0fb80-96e5-11eb-9bc0-eb5fd7b738ec.png)

An example of the interactive figure, zoomed in:
![mjp_pABRrates_000_V_zoomed](https://user-images.githubusercontent.com/15331606/113761356-59035580-96e5-11eb-90c7-8f1be0413e6b.png)
