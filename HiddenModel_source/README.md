# Hidden Model

The hidden model was based on Zarnitsyna VI, Bulusheva I, Handel A, Longini IM, Halloran ME, Antia R (2018). 
Intermediate levels of vaccination coverage may minimize seasonal influenza outbreaks. PLoS ONE 13(6): e0199674. 
[https://doi.org/10.1371/journal.pone.0199674](https://doi.org/10.1371/journal.pone.0199674).

The model is for two infectious agents, similar to Influenza A and Inflouenza B, with the possiblity of cross-infection and vaccinations.
<img width="912" height="455" alt="image" src="https://github.com/user-attachments/assets/bbcfce8a-402b-4e5a-9963-34f5d41023bc" />

The model was implmented in [COPASI](https://copasi.org/), which can be downloaded from [here](https://copasi.org/Download/).
The COPASI version of the model is available in this GitHub repo as `SIRCrossover_VZs_V2.cps`. The COPASI model includes three named parameter sets:

 1. `Fit_to_Data_InfA_2018`: A fit to CDC influenza data for 2018 (the data file is `influenzaA2017_2018.csv`.)
 2. `Leading_Hump`: Workshop Challenge 3
 3. `Trailing_peak`: Workshop Challenge 2

Use the navigation tree on the left of the COPASI window to navigate to `COPASI > Model > Biochemical > Parameter Sets`, then double click 
on a parameter set name, and in the resulting window click the "Apply" button in the lower right. The parameter set has now been loaded into the
model.

To run the model, navigate to `COPASI > Tasks > Time Course`, then click on the "Run" button at the bottom of the page. 
The simulation should run and open several windows, including "Hospitalizations". For the "Leading_Hump" parameter set the graph should look like:
<img width="641" height="498" alt="image" src="https://github.com/user-attachments/assets/dcf47817-19dc-49cc-b815-c05e8b82f9ea" />


J. Sluka<br>9 June 2026
