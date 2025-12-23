// import { getAllStoredChats, removeValueFromArray } from "../utils"
import {useState} from 'react'

function StoredChat(props){

    //NOTE - "frontend token" and "chat id" are used somewhat interchagebly here - 

    const {frontEndToken,setChatLogFunction,setCurrentChatIDFunction,currentChatID,allStoredChatsState,setAllStoredChatsFunction,currentChatLogState, index, chatSelectedFlag, setChatSelectedFlagFunction, getSpecificChatFunction} = props




    function replaceLastNCharacters(string,n){

        const choppedString = string.slice(0,-n)
        const replacementString = "x".repeat(n)

        const updatedString = choppedString + replacementString
        return updatedString




    }






    async function getSpecificChat (frontEndToken) {





            
            //get the specific chat from the chat history 
            const response = await fetch(`/get_chat_history/${frontEndToken}`,{
            method: 'POST'

            })

            if (response.ok){
                const data = await response.json()



                setChatLogFunction(data)
                setChatSelectedFlagFunction(true)
                setCurrentChatIDFunction(frontEndToken)
                

            }

    };


    const deleteChat = async () => {

        const confirmed = window.confirm("Are you sure you want to delete this chat?");
        console.log(`${allStoredChatsState}`)

        //get the previous frontend token compared to the one that's been selected
        const originalChatArraySize = allStoredChatsState.length

        // const previousChatID = allStoredChatsState[allStoredChatsState.length-2].frontend_token

        // //frontend token of the next element in the array
        const currentChatIndex = allStoredChatsState.findIndex(chat => chat.frontend_token ===frontEndToken )

        
        



        // const firstChatID = allStoredChatsState[0].frontend_token


        //if user changes mind about deleting chat and clicks 'no' when they are asked to confirm, delete the chat
        if (!confirmed) return;

        //if no chat currently selected, just delete it and don't select a chat

        

        



        if (!chatSelectedFlag) {
            const response = await fetch(`/delete_chat/${frontEndToken}`, {
            method: "DELETE",
            });

            if (!response.ok) return;

            setAllStoredChatsFunction(prev =>
            prev.filter(chat => chat.frontend_token !== frontEndToken)
            );

            if (allStoredChatsState.length === 1) {
            setChatSelectedFlagFunction(false);
            setChatLogFunction([]);
            setCurrentChatIDFunction(null);
            }

            return;
        }

        // //update the allStoredChats array
        // setAllStoredChatsFunction(prev =>
        // prev.filter(chat => chat.frontend_token !== frontEndToken)
        // );


        

        //if there is a chat that is currently selected selected
        else if(chatSelectedFlag){
            //placeholder for target chat ID after a chat is deleted 
            let targetChatID = null;

            //if there is more than one chat remaining before we delete it
            if(originalChatArraySize > 1){

                //if there exists a chat after the chat we are currently on
                if(currentChatIndex + 1 < allStoredChatsState.length) {
                    targetChatID = allStoredChatsState[currentChatIndex + 1].frontend_token


                }

                //if there is no chat after the one we are currently on and there is a chat before it - select the chat before
                else if (currentChatIndex - 1 >= 0) {

                    targetChatID = allStoredChatsState[currentChatIndex - 1].frontend_token

                }


                const response = await fetch(`/delete_chat/${frontEndToken}`, {
                method: "DELETE",
                });


                setAllStoredChatsFunction(prev =>
                 prev.filter(chat => chat.frontend_token !== frontEndToken)
                );

               

            }
            if(targetChatID){
                 await getSpecificChat(targetChatID)
            }
            
            //if we delete the last chat
            else {

                const response = await fetch(`/delete_chat/${frontEndToken}`, {
                method: "DELETE",
                });


                setAllStoredChatsFunction(prev =>
                 prev.filter(chat => chat.frontend_token !== frontEndToken)
                );

                //set the chatSelected state false to indicate that no chat is selected
                setChatSelectedFlagFunction(false)
                //display an empty chat log
                setChatLogFunction([])
                //set the current chat id value null
                setCurrentChatIDFunction(null)

            }




        }

        

        
    };


    
    return (
        <>
            
            <button className={`chat-preview-block  ${currentChatID===frontEndToken ? "chat-selected":""}`} onClick={()=>{getSpecificChat(frontEndToken)}}>
                <p> Chat: {frontEndToken ? index:"New chat..."}</p>

                    <p onClick={deleteChat} className={`delete-chat-button`}><i class="fa-solid fa-trash-can"></i></p>

            </button>



            
        
        
        
        </>
    )

}






export default StoredChat;