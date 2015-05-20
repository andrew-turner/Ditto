from .commands import *

def toCommands(node):
   """
   Turn an AST into a command list.

   node - the node of the AST to start at.
   """

   #initialise command list
   cmds = []

   #if we have a statement list, iterate over each statement and add it to the commands
   if node.kind == "STATEMENTLIST":
      for child in node.children:
         cmds += toCommands(child)

   #if we have a print statement, add a print command
   elif node.kind == "PRINT":
      exprNode = node.children[0]
      cmds.append([CMD_PRINT, exprNode])

   #if we have an assign statement, add an assign command
   elif node.kind == "ASSIGN":
      idChainNode, exprNode = node.children
      cmds.append([CMD_ASSIGN, idChainNode, exprNode])

   #if we have an assigncommand statement, add an assigncommand command
   elif node.kind == "ASSIGNCOMMAND":
      idChainNode, commandNode = node.children
      cmds.append([CMD_COMMANDASSIGN, idChainNode, commandNode])

   #if we have a commandcall statement, add a commandcall command
   elif node.kind == "COMMANDCALL":
      commandNode = node.children[0]
      idChainNode, argListNode = commandNode.children
      cmds.append([CMD_COMMANDCALL, commandNode])

   #if we have an if statement, determine whether there's an else clause or not
   elif node.kind == "IF":
      
      #if there's no else, then add an eval command followed by an iffalsegoto and then the conditional commands
      if len(node.children) == 2:
         exprNode, trueNode = node.children
         trueCmds = toCommands(trueNode)
         cmds.append([CMD_EVAL, exprNode])
         cmds.append([CMD_IFFALSEGOTOREL, len(trueCmds)])
         cmds += trueCmds

      #if there's an else, then then add an eval command followed by an iffalsegoto and then the true commands
      #then put in a gototo skip over the false commands, and then put the false commands
      elif len(node.children) == 3:
         exprNode, trueNode, falseNode = node.children
         trueCmds = toCommands(trueNode)
         falseCmds = toCommands(falseNode)
         cmds.append([CMD_EVAL, exprNode])
         cmds.append([CMD_IFFALSEGOTOREL, len(trueCmds)+1])
         cmds += trueCmds
         cmds.append([CMD_GOTOREL, len(falseCmds)])
         cmds += falseCmds         

   #return the commands
   return cmds   
