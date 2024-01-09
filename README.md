
arkouda server version = v2023.11.15+23.g663260519  
Client Version: v2023.11.15+23.g663260519

2.2

#Please make sure the SPX_500_Data.csv file and the market_analysis.py script are in the same directory

Objective: I picked the following dataset because it is quite large in size and covers S&P data all the way from the 1920's with 18,000 + rows.
My thinking is that size and variance of features in this dataset would lend itself to show the efficiency of carrying out operations that are somewhat
expensive from a computational perspective. Some areas I chose to focus on included monotonticity analaysis in terms of daily returns, volalitlty analysis, visualization and feature statsitics (to name a few).

## What the code does?
- Computes daily average returns based on the close price
- Computes volatility based on a 20 day rolling/sliding window
- Plots both of these distributions using matplotlib
- Finds monotontic trends in terms of daily returns
- Uses the arkouda groupBy function to catergorize each days voalitlity into either "High" "Low" based on a threshold
- then calculates the average daily returns of each of those groups.
- Computes some simple stastisics for each column.

  #The code takes on average 2-3 minutes to fully run


2.3
1. The module_configuration.py file can be used to build the executable similar to arkouda

    Some commands that need modification are 
* --pkg_path -p: This needs to be set to the path of the Arachne module.
* --ak_loc  -a: This should be set to the path of the Arkouda installation
*  --config_loc or -c: If you prefer to store temporary configuration files in a different directory than the 
* --from_file: If you're providing a text file listing multiple packages to be installed, you would use this flag.  
* --from_parent: : This flag is used if you're specifying a directory containing multiple packages

Commands outputted:

Pip Install Command:
print(f"pip install -U {' '.join(PIP_INSTALLS)}")
This command installs or updates the client-side Python packages found in the PIP_INSTALLS list.

Copy Configuration Command:
print(f"cp {ak_cfg} {tmp_cfg}")
Copies the existing Arkouda ServerModules.cfg file to a temporary file for modification.

Make Command:
print(f"ARKOUDA_SERVER_USER_MODULES={ak_srv_user_mods} ARKOUDA_CONFIG_FILE={tmp_cfg} ARKOUDA_SKIP_CHECK_DEPS=true make -C {ak_loc}")
This command builds the Arkouda server with the new module configurations. 



The ServerModules.cfg file  is used to list and register various server-side modules that need 
to be included when building the server executable. In the context of Arachne, this 
would include modules such as BuildGraphMsg, GraphInfoMsg, BreadthFirstSearchMsg, PropertyGraphMsg, 
TriCtrMsg, TriangleCountMsg, SquareCountMsg, TrussMsg, and ConnectedComponentsMsg


2.
The function that gives the Arkouda server knowledge of the segSquareCountMsg procedure is
registerFunction().T he line registerFunction("segmentedGraphSquares", segSquareCountMsg,
getModuleName()); registers the segSquareCountMsg procedure with a command name 	"segmentedGraphSquares"
MessageArgs object ,this object is essential for interpreting messages sent from the Python client.
Within the segSquareCountMsg procedure, the MessageArgs object, referred to as msgArgs, plays a
crucial role. It holds the arguments transmitted from the Python side. The procedure utilizes functions
like msgArgs.getValueOf("GraphName") and msgArgs.getValueOf("DegreeName") to extract specific data from the incoming message.

3.The squares function. This function corresponds to the square counting functionality in the Chapel code 
SquareCountMsg.chpl.  Yes the command arguments are the same args = { "GraphName" : graph.name,"DegreeName" : degree.name }. 
Arkouda is facilitating this message transmission 	using client-server model, where the Python API acts as the client 
sending requests to the Chapel-	based server. The generic_msg function in the Python API is a part of the Arkouda package and is 		
designed to handle the communication between the Python client and the Chapel server

4. Create a Chapel module for the operation logic, named Foo.chpl. 
This file would contain the implementation of the foo operation. 
Create a Chapel message module to handle server communication, 
named FooMsg.chpl. This file would define how the Arkouda server processes 
and responds to messages related to the foo operation. In the Python API for Arachne, create a function named foo. 
This function would be responsible for constructing and sending the appropriate message to the Chapel server and 
handling the response. In the ServerModules.cfg file would add FooMsg as one line. The last line used in the FooMsg.chapel 
file would be registerFunction("foo", fooMsgFunction, getModuleName());

5. Arkouda and Arachne persist data across the lifetime of an Arkouda server using a Symbol Table to store objects.  
	 From the provided SquareCountMsg.chpl script, the extraction from the symbol table can be 	identified in the following lines:
	chapel
	
  //Pull out our graph from the symbol table. 

	var gEntry: borrowed GraphSymEntry = getGraphSymEntry(graphEntryName, st);
	 var g = gEntry.graph; 

	// Pull out degree graph from the symbol 	table. 

	var degree_entry: borrowed GenSymEntry = getGenericTypedArrayEntry(degreeName, st); 
	var 	degree_sym = toSymEntry(degree_entry,int);
	 var 	degree = degree_sym.a;





  
