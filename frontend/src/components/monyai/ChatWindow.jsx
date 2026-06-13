import {useState, useEffect, useRef} from 'react'
import '../../index.css'
import StoredChat from './StoredChat';
import { getAllStoredChats } from '../../utils';
import { BASE_URL } from '../../api';

import { useAuth } from '../../context/AuthContext';
import { useChatStreamContext } from '../../context/ChatContext';
import {toast} from 'react-hot-toast'
import SourcesModal from './SourcesDisplayModal';
import ReactMarkdown from 'react-markdown'
function ChatWindow() {

    const [userInput, setUserInput] = useState('');
    const [chatLog, setChatLog] = useState([]);
    const [loading, setLoading] = useState({});
    //boolean to check if a chat has been selected or not
    const [chatSelectedFlag,setChatSelectedFlag] = useState(false);
    //list of all chats created by the user
    const [allCreatedChats,setAllCreatedChats] = useState([]);

    /*the conversation id of the current selected chat (not the conversation id of the backend)
     triggers rerender when active chat changes. Need so tha UI correctly highlights selected chat...
    and show the correct messages*/

    const [currentChatID,setCurrentChatID] = useState(null); 
    
    /* Check if current chat ID has been changed - used to detect a change before rerender */
    const currentChatIDRef = useRef(null);

    //check if user is currently creating a chat or not
    const [creatingChat, setCreatingChat] = useState(false)

    const [showSourcesModal,setShowSourcesModal] = useState(false)

    const [userErrorMessage,setUserErrorMessage] = useState("")



    const chatWindowBottomRef = useRef(null);





    //const queryID
    const [queryID, setQueryID] = useState(null)


    //controllerRef flag to indicate that
    const controllerRef = useRef(false)

    //tracking if user has pressed the cancel button
    const cancelledRef = useRef(null);

    const {globalUser,logout,fetchWithAuth} = useAuth()

    // consume chat stream context - buffer streams per conversation so switching chats mid-stream doesn't lose data
    const { appendStringToBuffer, finalizeBuffer, removeBuffer, bufferRef } = useChatStreamContext()
    const [sidebarOpen, setSidebarOpen] = useState(false)

    const [messageSources,setMessageSources] = useState("")
    // Load chat history for the current selected chat
    useEffect(() => {


    }, []);


    //Load previously created chats
    useEffect(()=>{




         getAllStoredChats(setAllCreatedChats,fetchWithAuth);
         console.log(allCreatedChats)
        

    },[])


    useEffect(()=>{

        // mirrors currentChatID state so the async stream loop can read the latest value without a stale closure

        currentChatIDRef.current = currentChatID;

    },[currentChatID])


    async function handleShowSources (sources) {

        // handle showing the references

        setShowSourcesModal(true); 
        setMessageSources(sources)



    }


    //every time a new message is in the chat, or a different chat is selected, scroll to the bottom of the chat area (everytime chatlog changes)
    useEffect(()=>{

        if(chatWindowBottomRef){
            chatWindowBottomRef.current.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'start' })

        }



    },[chatLog])

    //remove specific item from array
    function removeItem(array, valueToRemove) {
        return array.filter(
    	item => item !== valueToRemove);
    }




    //Load all stored chats into local storage


    const clearChatHistory = async (event) => {
        event.preventDefault();
        try{
            const response = await fetchWithAuth(`/api/clear_chat`, {
                method: 'POST',
                body: JSON.stringify({
                    conversation_id: currentChatID

                }),

            });

            if(response.ok){

                // setChatLog([{ type: 'bot', message: userInput,timestamp:String(now)])
                //get the specific chat from the chat history 
                const response = await fetchWithAuth(`/api/get_chat_history`,{
                method: 'POST',
                body: JSON.stringify({conversation_id:currentChatID}),


                })
                const chatData = await response.json()

                setChatLog([chatData[0]])
                await getAllStoredChats(setAllCreatedChats,fetchWithAuth)
                
                
            }
            

            


        }
        catch (error) {
            console.error("Failed to clear chat",error)
        }

    }

    async function createNewChat(event) {

        //if user not logged in, block creating a new chat
        if(!globalUser) {
            toast.error(` Please log in again to use the chatbot`,);
            return
            
        };

        event.preventDefault();
        setCreatingChat(true)

        //add the new chat to the database
        const response = await fetchWithAuth("/api/create_new_chat",{
            method: "POST"

        })

        //get the data about the chat and convert to json
        const data = await response.json()
        //get the updated list of chats
        await getAllStoredChats(setAllCreatedChats,fetchWithAuth)

        setCreatingChat(false)

        return data.conversation_id

        

    }





    //function to cancel generating an answer
    const handleCancelResponse= async (event) =>{
        event.preventDefault()

        //set the cancelled reference to true
        cancelledRef.current = true;
        //abort the original API request 
        controllerRef.current?.abort()
 
        //reset states
        setLoading((prev)=>({...prev, [currentChatID]: false}))
        setUserInput("")
        // clear the buffer for the cancelled conversation
        removeBuffer(currentChatID)
        setChatLog((prev) => {

            //creating shallow copy of chat log and removeing the last two elements (i.e. deleting the last user query and partially generated text from chatbot)
            const updatedChatlog = [...prev].slice(0,-2)

            // const latestUserQuery = updatedChatlog[updatedChatlog.length - 2]

            // //get the latest entry of the chat log (will have the blank text)
            // const latestMessage = updatedChatlog[updatedChatlog.length - 1]
            return updatedChatlog


        }); 

        //get cancel endpoint (with specific query id)
        const cancelEndpoint = `${BASE_URL}/api/cancel_response/${queryID}`
        fetch(cancelEndpoint,{
            method: "POST"
        }).then(res=>res.json()).then(console.log("cancelled")).catch(err => console.error("Failed to cancel", err));

        //delete that last message generated by the bot and the last query sent by the user from the chat log




        }
    

    async function streamChatbotAnswer(conversationId){

                //get the timestamp for when the message was sent
        const now = new Date().toISOString()
        // Don't allow user to send an empty message
        if (!userInput.trim()) return; 

        const userMessage = { type: 'user', message: userInput,timestamp:String(now) };

        
        // update chat log array 
        const newChatLog = [...chatLog, userMessage];
        setChatLog(newChatLog);
        setUserInput('');
        setLoading((prev)=>({...prev, [conversationId]: true}));

        // clear any existing buffer for this conversation before starting a new stream
        removeBuffer(conversationId)

            //browser api class which is used to cancel api requests 
            const controller = new AbortController()
            //saving this specific instance of abort controller - can call without rerender - access DOM directly
            //setting the global controller ref to this instance of the abort controller
            controllerRef.current = controller

            //returns an abort signal object instance to communicate with or abort an async operation - in this app, using it for 'cancelling'
            const signal = controllerRef.current.signal;
            cancelledRef.current = false;
    

        try {
            // The API call to our FastAPI backend
            const response = await fetchWithAuth("/api/chat", {
                method: "POST",

                body: JSON.stringify({
                    user_message: userMessage,
                    // strip reference_docs before sending — backend expects str|None but we store it as a parsed array for the UI
                    chat_history: newChatLog.map(({ reference_docs, ...msg }) => msg),
                    client_form: null,
                    conversation_id: conversationId
                }),

                signal: signal
                
            });

            //get the the query ID of the user input
             const chatInputQueryID = response.headers.get("X-Query-ID")


             setQueryID(chatInputQueryID)

            


            if (response.ok){

                //read input data as a stream
                const reader = response.body.getReader()


                //create text decoder to decode binary data into text
                const decoder = new TextDecoder("utf-8")

                //checking to see if streaming done
                let done = false;

                const now =  new Date().toISOString()

                // Add an empty bot message to the chat log before the text streaming starts
                setChatLog(prev => [...prev, { type: 'bot', message: '', timestamp: String(now) }]);

                // flag to track whether we've seen __REFS__ yet
                let refsStarted = false;
                // collects all refs/sources text across multiple chunks — built up until stream ends then parsed as JSON
                let refsBuffer = "";
                // accumulates every chunk of raw text received so far — kept outside the loop so it persists across chunks,
                // allowing __REFS__ to be detected even if it arrives split across two separate chunks
                let rawResponseBuffer = ""

                while(!done){

                    const {value, done: readerDone} = await reader.read()

                    done = readerDone
                    if(done) {
                        // stream ended — finalize refs with everything collected in refsBuffer
                        if(refsStarted){
                            finalizeBuffer(conversationId, refsBuffer)
                            if(currentChatIDRef.current === conversationId){
                                setChatLog((prev)=>{
                                    const updatedChatlog = [...prev]
                                    const latestMessage = updatedChatlog[updatedChatlog.length - 1]
                                    if(latestMessage.type === 'bot'){
                                        updatedChatlog[updatedChatlog.length - 1] = {
                                            ...latestMessage,
                                            reference_docs: JSON.parse(refsBuffer)
                                        }
                                    }
                                    return updatedChatlog
                                })
                            }
                        }
                        break
                    };

                    if(value){
                        const chunkValue = decoder.decode(value,{stream: true})

                        // once __REFS__ has been seen, every subsequent chunk is refs text — add to refsBuffer and skip message logic
                        if(refsStarted){
                            refsBuffer += chunkValue
                            continue
                        }

                        // add this chunk to the running total of all text received so far
                        rawResponseBuffer += chunkValue

                        // check the full accumulated text (not just this chunk) for __REFS__ so we catch it even if it was split across two chunks
                        if(!refsStarted && rawResponseBuffer.includes("__REFS__")){
                            // first time we see __REFS__ marker...
                            // ... split the chunk, append any message text before it, start collecting refs after it
                            refsStarted = true
                            //split buffer into an array of two parts - [0] is response text, [1] is sources
                            const parts = rawResponseBuffer.split("__REFS__")
                            // parts[0] is all message text so far — sync it into the text display buffer
                            appendStringToBuffer(conversationId, parts[0])
                            refsBuffer = parts[1] ?? ""
                        } else {
                            // normal message chunk  : append to buffer regardless of which chat is active to prevent data loss when switching chats mid-stream
                            appendStringToBuffer(conversationId, chunkValue)

                            // only update the displayed chat if this is the currently viewed chat
                            if(currentChatIDRef.current===conversationId){
                                setChatLog((prev)=>{
                                    const updatedChatlog = [...prev]
                                    const latestMessage = updatedChatlog[updatedChatlog.length - 1]
                                    if(latestMessage.type === 'bot'){
                                        updatedChatlog[updatedChatlog.length - 1] = {
                                            ...latestMessage,
                                            message: bufferRef.current[conversationId]?.text ?? ""
                                        }
                                    }
                                    return updatedChatlog
                                });
                            }
                        }
                        

                    }


                }


                // Ensure final version of chat is saved after stream finishes - save to local storage for persistence
                setChatLog(prev => {
                const finalChat = [...prev];
                // sessionstorage.setItem('chatLog', JSON.stringify(finalChat));
                return finalChat;
                });
                

            }

            else if (!response.ok) {
                

                //if we get a rate limit error
                if(response.status === 429){
                    const data = await response.json()
                    console.log
                    const message = data.message
                    
                    setUserErrorMessage(`${message}`)
                    toast.error(message)
                    return
                }
                throw new Error(`HTTP error! status: ${response.status}`);
            }

        } catch (error) {
            console.error('Error fetching chat response:', error);

            //ignore abort errors as this is when the user cancels
            if(!error.name === "AbortError"){
                const now =  new Date().toISOString()
                //if connection fails for any other reason, show in the chat that 'Something went wrong' 
                const errorMessage = { type: 'error', message: 'Sorry, something went wrong. Please try again.',timestamp: String(now) };
                setChatLog(prev => [...prev, errorMessage]);

            }
            
        } finally {
            setLoading((prev)=>({...prev, [conversationId]: false}));
            // clear buffer after short delay — gives time for final chatLog update to complete before removing buffer
            setTimeout(() => removeBuffer(conversationId), 2000)
        }


    }
    


    const handleSubmit = async (event) => {
        event.preventDefault();
        
        // //if chat not yet selected (i.e. user just starts typing without selecting chat first)
        if(!chatSelectedFlag){
            //create a new chat id 
            const newChatID = await createNewChat(event)


            //get the specific chat based on chat ID
            const response = await fetchWithAuth(`/api/get_chat_history`,{
            method: 'POST',
            body: JSON.stringify({conversation_id:newChatID}),

            })

            if (response.ok){
                const data = await response.json()
                console.log(data)
                //set the chatlog to the current selected chat
                setChatLog(data)
                setCurrentChatID(newChatID)
                currentChatIDRef.current = newChatID  // immediate sync


                // send message to newly create chat, stream answer from chatbot
                await streamChatbotAnswer(newChatID)
                

            }
            
            
            setChatSelectedFlag(true)

            }
        else {

            // send message to selected chat, and stream the answer from the chatbot
            await streamChatbotAnswer(currentChatID)

        }

        

    

    };






    return (

            <div className='main-chatbot-container'>
                <SourcesModal showSourcesModal={showSourcesModal} setShowSourcesModalFunction={setShowSourcesModal} sourcesForCurrentMessage={messageSources}/>
                <button className="hamburger-button" onClick={() => setSidebarOpen(!sidebarOpen)}>
                    {sidebarOpen ? '✕' : '☰'}
                </button>

                <div className={`chat-selection-container${sidebarOpen ? ' sidebar-open' : ''}`}>
                    <img  src='/twt-logo.png' className='twt-logo'/>
                    <button disabled={creatingChat} onClick={(event)=>createNewChat(event)}>
                        + New Chat
                    </button>
                    {creatingChat &&<div className='creating-chat-message'>Creating new chat... </div>}
                    <div className='all-chats-container'>
                        
                        {allCreatedChats.map((storedChat,index)=>(

                                <StoredChat key={String(index)+storedChat.conversation_id} index = {index+1} conversationId = {storedChat.conversation_id} setChatLogFunction={setChatLog} setCurrentChatIDFunction={setCurrentChatID} currentChatID={currentChatID} setAllStoredChatsFunction={setAllCreatedChats} currentChatLogState={chatLog} chatSelectedFlag={chatSelectedFlag} setChatSelectedFlagFunction={setChatSelectedFlag} allStoredChatsState={allCreatedChats} currentChatRef = {currentChatIDRef}/>
                            ))}

                    </div>
                </div>

                
                <div className='chat-area'>
                        
                    <div className="chat-window">
                        {chatLog.map((message, index) => (
                            <div key={`${message.timestamp}-${index}`}>
                                <div className={`message ${message.type}`}>
                                    <ReactMarkdown>{message.message}</ReactMarkdown>
                                </div>

                                {<p className='message-timestamp'>{String(message.timestamp).substring(8,10)+ "/"+ String(message.timestamp).substring(5,7)+"/"+String(message.timestamp).substring(0,4)+" "+String(message.timestamp).substring(11,16)}</p> } 
                                {/** If the message is from the chatbot (excluding initial greeting)*/}
                                {(message.type == 'bot' && message.message !=="" && !loading[currentChatID] && index > 0)&&(
                                    <button className='show-sources-button' onClick={()=>{handleShowSources(message.reference_docs)}}>View Sources</button>


                                )}
        
                            </div>
                        
                        ))}

                        <div ref={chatWindowBottomRef}></div>
                        
                    </div>

                    {!loading[currentChatID] && <button className="cancel-query-button" onClick={clearChatHistory}>Clear chat history</button>}
                    { loading[currentChatID] && <button className="cancel-query-button" onClick={handleCancelResponse} type="submit" >Cancel</button>}
                    
                    { userErrorMessage && <div className="cancel-query-button" >{userErrorMessage}</div>}
                    
                    <form onSubmit={handleSubmit} className="chat-form">

                        <input
                            type="text"
                            value={userInput}
                            onChange={(e) => setUserInput(e.target.value)}
                            placeholder="Enter your question"
                            disabled={loading[currentChatID] || creatingChat}
                        />
                        <button className="send-query-button" type="submit" disabled={creatingChat||loading[currentChatID]||userInput==""}><i className="fa-solid fa-paper-plane"></i></button>
                    </form>
                    

                </div>

            </div>

        
        
        
    )

}



export default ChatWindow;