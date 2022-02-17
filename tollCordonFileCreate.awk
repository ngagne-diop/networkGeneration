# script pour générer le peage
# Authors: Ousmane Diop and Ngagne Diop
# Date: May 2021
# Last edited: May 2021

BEGIN {
  FS=";";

# entête obligatoire pour MATSim
  {print "<?xml version=\""1".0\" encoding=\"utf-8\"?>"}
 # {print "<!DOCTYPE plans SYSTEM \"http://www.matsim.org/files/dtd/plans_v4.dtd\">"}
  {print "<!DOCTYPE roadpricing SYSTEM \"http://www.matsim.org/files/dtd/roadpricing_v1.dtd\">"}
  {print ""}
  {print "<roadpricing type=\"link\" name=\"LilleCordonToll\">"}
  {print "	<links>"}
 }

{
## position id_link
  id_link=$7;
        #print "       				<cost start_time=\""05":00\" end_time=\""10":00\" amount=\"10.\" />"
		
  if (NR>=2) {
        print "		<link id=\""id_link"\"/>";		
        #print "		</link>";
        }

}


END{

  {print "	</links>"}
  {print "        <cost start_time=\""06":00\" end_time=\""10":00\" amount=\"1.\" />"}
  {print "        <cost start_time=\""10":00\" end_time=\""15":00\" amount=\"0.5\" />"}
  {print "        <cost start_time=\""15":00\" end_time=\""19":00\" amount=\"1.\" />"}
  {print "</roadpricing>"}
}
