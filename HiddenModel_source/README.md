# Hidden Model

The hidden model was based on Zarnitsyna VI, Bulusheva I, Handel A, Longini IM, Halloran ME, Antia R (2018). 
Intermediate levels of vaccination coverage may minimize seasonal influenza outbreaks. PLoS ONE 13(6): e0199674. 
[https://doi.org/10.1371/journal.pone.0199674](https://doi.org/10.1371/journal.pone.0199674).

The model is for two infectious agents, similar to Influenza A and Inflouenza B, with the possiblity of cross-infection and vaccinations.
<img height="350" alt="image" src="https://github.com/user-attachments/assets/bbcfce8a-402b-4e5a-9963-34f5d41023bc" />

The model was implmented in [COPASI](https://copasi.org/), which can be downloaded from [here](https://copasi.org/Download/).
The COPASI version of the model is available in this GitHub repo as `SIRCrossover_VZs_V2.cps`. The COPASI model includes three named parameter sets:

 1. `Fit_to_Data_InfA_2018`: A fit to CDC influenza data for 2018 (the data file is `influenzaA2017_2018.csv`)
 2. `Leading_Hump`: Workshop Challenge 1
 3. `Trailing_peak`: Workshop Challenge 2

Use the navigation tree on the left of the COPASI window to navigate to `COPASI > Model > Biochemical > Parameter Sets`, then double click 
on a parameter set name, a popup will warn that you are overwriting current model values, and normally you would click on the "Discard" 
button unless you want to save the old parmater values. In the next window click the "Apply" button in the lower right. 
The parameter set has now been loaded into the model.

To run the model, navigate to `COPASI > Tasks > Time Course`, then click on the "Run" button at the bottom of the page. 
The simulation should run and open several windows, including "Hospitalizations". 

For the `Leading_Hump` parameter set the graph should look like:

<img height="300" alt="Leading_Hump parameter set the graph" src="https://github.com/user-attachments/assets/dcf47817-19dc-49cc-b815-c05e8b82f9ea" />

<br><br>

For the `Trailing_peak` data set, the graph should look like:

<img height="300" alt="Trailing_peak parameter set the graph" src="https://github.com/user-attachments/assets/25ebb159-d14f-4701-82b0-3fa8414cb9a9" />

<br><br>

For the `Fit_to_Data_InfA_2018` parameter set the graph should look like:

<br><br>

<img height="300" alt="Fit_to_Data_InfA_2018 parameter set the graph" src="https://github.com/user-attachments/assets/91d23296-2b11-466e-9383-943bd44700bf" />

<br><br>

The COPASI file is also setup to fit the `Fit_to_Data_InfA_2018` data. Navigate down to `COPASI > Tasks > Parameter Estimation`. 
 * The CDC data is already linked to the parameter estimation task, and you can examine that linkage by clicking the "Experimental Data" button in the upper right.
    * You can choose the optimization method with the "Method" dropdown near the center of the page.
    * "Particle Swarm" works well and is less likely to get trapped in a local minima.
    * Click on the "Show Settings" checkbox and change the swarm settings to Iteration Limt: 10000, Swarm Size: 2000, and Std. Deviation: 1e-9.
* Click the "Run" button at the bottom of the page.
* Several windows should open including "Progress of Fit" and "COPASI Progress Dialog". (These windows may be hidden behind the main COPASI window.)
    * This model has several feedback loops so it is easy for it to get trapped in a local minima.
    * You might run the swarm several times and choose the one that gives the lowest sum of squares error.
    * For this model and data set, the error should be around 2.3.

<img height="300" alt="image" src="https://github.com/user-attachments/assets/8df4d24c-fbd7-47fa-a196-e200735e06f2" />


J. Sluka<br>9 June 2026
