/sc:spec-panel                                               
  <Context> I am building an opencode custom command and       
  accompanying agents and tooling to take                      
  rough ideas from a user and through Q&A, research, best      
  practices, templates and anything else                       
  needed, collaborate and expand on and ultimately refine      
  the initial idea into a gold-standard                        
  quality spec to be used to generate  project or feature      
  roadmap as per the roadmapping m ethodology                  
  found <project-root>/.dev/releases/backlog/v
  .4.1-roadmap-gen </context>                                  
  <Objectives>                                                 
  - To deeply research and extract all of the methodologies,   
  strategies, best practices and workflows                     
  of the /sc:spec-panel custom command into a markdwon         
  document that will form the contextual                       
  foundation to recreate and improve upon the /sc:spec-panel   
  command but in opencode instead of                           
  claude code.  All claude code specific references or         
  dependencies must be first catelogued and then               
  researched must be done on each one to determine exactly     
  how to achieve the same results in open                      
  code, with each proposed solution undergoing an              
  adversarial debate for validation                            
  - To add the additional execercise we just did above         
  around thinking through, discussing and                      
  ultimately groking the higher level objectives behind        
  lower level ideas, goals and improvements                    
  laid out by the user                                         
  - To ultimately use this much clearer understanding of the   
  high level motivations behind the spec                       
  to formulate more expansive question sets and to enable      
  the agents to build upon the idea with the                   
  user, aiming to expand and improve  it, challenging it and   
  ultimately finding additinoal and better                     
  ways to achieve the high level objectives.                   
  </Objectives>                                                
  <tasK>                                                       
  - Use chain of thought reasoning to determine all of the     
  dependencies needed to achieve the                           
  objectives above                                             
  - Initiate an exhaustive research project for each           
  dependencies, spinning up a parallel agent for               
  each using the /sc:research custom command, saving the       
  relevant findings to an .md file                             
  - Once the above 2 tasks are complete, generate me a         
  concide but comprehensive prompt that uses the               
  /sc:spec-panel that will generate a spec for the complete    
  porting and improvement of the /sc-panel                     
  command over to opencode                                     
  </task>   The resulting spec will become the spec for        
  @.dev/releases/backlog/v.4.0-Spec-generator-framework/ 

  sc:spec-panel
  - Spawn multiple agents, 1 for each new feature or improvement,
  Review @.dev/releases/current/v0.5/0.5-SpecDraft01.md and use
  chain of thought reasoning to theorize the higher level needs
  and objectives of these improvements. Not necessarily high level needs of a specific type(ie: business) but looking for the broader motivations of the stakeholder or department.  The AI Agent can take a best guess at who the primary stakeholder department is: Business Development, Engineering, Management/Operations and the user can confirm one or morel
   -- For example, the low level objective might be "Shows date +
  per-developer breakdown (Danikami: 23, Grigory: 12, Hazem: 8)"
  however the high level objective would be "To gain a more
  granular clarity and causes of trends or changes in trends