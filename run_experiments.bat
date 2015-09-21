rem ----------------------------------------------------------------------------
rem This file runs the experiment scenarios contained in the params folder.
rem ----------------------------------------------------------------------------

python scenario_runner.py ./params/scen_m_m_m.csv
python scenario_runner.py ./params/scen_m_m_p.csv
python scenario_runner.py ./params/scen_m_p_m.csv
python scenario_runner.py ./params/scen_m_p_p.csv
python scenario_runner.py ./params/scen_p_m_m.csv
python scenario_runner.py ./params/scen_p_m_p.csv
python scenario_runner.py ./params/scen_p_p_m.csv
python scenario_runner.py ./params/scen_p_p_p.csv