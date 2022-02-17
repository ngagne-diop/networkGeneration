# script pour générer le peage
# Authors: Ousmane Diop and Ngagne Diop
# Date: May 2021
# Last edited: May 2021

BEGIN {
  FS=",";

# entête obligatoire pour MATSim
  {print "<?xml version=\""1".0\" encoding=\"utf-8\"?>"}
  {print "<!DOCTYPE roadpricing SYSTEM \"http://www.matsim.org/files/dtd/roadpricing_v1.dtd\">"}
  {print ""}
  {print "<roadpricing type=\"link\" name=\"linkToll\">"}
  {print "	<links>"}
 }

{
## position id_link
  id_link=$1;
  a=$2;

  if (NR>=2) {
        print "		<link id=\""id_link"\">";

        print "       				<cost start_time=\""00":00\" end_time=\""30":00\" amount=\""a"\" />"
        print "		</link>";
        }

}


END{

  {print "	</links>"}
  {print "        <cost start_time=\""00":00\" end_time=\""30":00\" amount=\"0.\" />"}
  {print "</roadpricing>"}
}
