# HyProNet - Hybrid Process Networks Modelling and Optimization PLatform

Our project is a domain independent software platform for modelling and optimization of network systems.  It is comprised of GUI (written in extended Reactflow), database to store network representations and its specifications (implemented in MongoDB), business intelligence tools for displaying and analyzing results of the computations (implemented in MetaBase), and database to store results of multi-period model computations (implemented in PostgreSQL). The user interface for a model is represented by a network of nodes and edges that the user can freely modify and edit. 

Attributes of the network arcs correspond to the domain being modelled, e.g. 
   for a chemical plant an arc may represent a streamm described by flow, temperature, pressure, chemical component names, and component flows; or it can be an energy stream (electric or thermal)
   for  gasoline blending netwokr, each arc would be described by RON, MON, RVP, etc.
   for an electric distribution network each arc may be described by volate, current, phase, etc.

Domain attributes are described in system tables. GUI is domain independent, i.e. the attributes displayed in the GUI are the  attributes that are specified in the system table for the corresponding domain.

It is assumed that a user will first define a base model capable of simulation the network behavior, ensure is correctness via computation, and then save the network as a "verified network".  Once the network is verified, a user can proceed to define multi-period model.  Both, single-period and multi-period netwokr can be calculated either in a simulation mode (specify inputs and node parameters) or in an optimization mode (free some variables, define objective function and cost coefficients).

Each node in the network has ports; each port is assigned a port class (defined by specific attributes).  Icon for the nodes are also specified in system tables (size, location of ports, color of the ports), which makes it easy for a user to add a new node model.  We can think of a node as being comprised of a "frame" (defined ports and attributes carried by each port), name of the node model and a version of the node model.  Each node model can have several versions.  User can choose via GUI which model version to use for a specific node and for a specific period in a multiperiod model.

Node data definition (NDD) tables specify number of ports and port class for each port, mapping of port attributes (variables) to internal names of the model variables.  That makes it possible to use short, meaningful names in the model code.  Every node also has an "information" port which is used to store all intenral node model parameters and variables.  In addition, NDD tabels specify which variables are fixed in simulation mode (e.g. flows from a source node), which is then treated as a required node input in the GUI.

In order to remain domain independent, it is assumed that a user will provide attributes for each arc in the network.  For instance, for a chemical plant, a user needs to provide temperature, pressure, unit enthalpy at tehse T & P, component names and component fractions.  Our particular implementation assumes that stream flows and componentn flows are in mass units.

Unlike traditional network modelling software, we provide capabilities to define multi-phase solution algorithms.  For each phase of the algorithm, a user can specify which set of node equations is to be instantiated.  In addition after each pahse user can specify the name of the node specific function to be executed for each node after that pahse.  That enables e.g. updating node parameters from more accurate model.

The only part of the code that is domain specific are the node models that know what to do with the attributes carried by the ports.  

Calculational server is written in Pyhton/PYOMO.  

If someone wanted to model e.g. electric distribution network and use JuMP instead of Python/PYOMO, they would have to write node models in JuMP and re-write assembling the entire network model equations )Cals Server) in JuMP.

High level view of the HyProNet architecture is given in the figure below.

![Hyproent Architecture August 2026](./images/example.png)



Domain Independent Software Platform Developer Names: 

Alpha version: 2024/25 Kishor Pandya, Dhrumil Pandya, Madhu Sivapragasam, Rasik Pokharel (capstone for Team 18: Chemware Engineering for the course SFWRENG 4G06 at McMaster University).

Beta 1 version: 2025: Jinjing Zhai, Mingyi Hou, Mitreya Korekar, Songming Liu -M.Eng. project for Master of Systems and Technology degree.

Beta 2 version: 2026: Kun Jiang, Tianyu Zhang, Muyao Guo, Hongyu JIang, Ricardo Corrales  -M.Eng. project for Master of Systems and Technology degree. 

Calculational Server developer: Farbod Maghsoudi

Node Model Developer for Hydrogen Plant: Raunak Pandey

Supervisor: Prof. Vladimir Mahalec

Date of project start: September 11th 2024

The folders and files for this project are as follows:

docs - Documentation for the project
refs - Reference material used for the project, including papers
src - Source code
test - Test cases
etc.
