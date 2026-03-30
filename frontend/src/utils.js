

export async function getAllStoredChats(setAllCreatedChatsFunction,fetchWithAuthFunction){



  try {
    
    const response = await fetchWithAuthFunction("/api/get_stored_user_chats", {
      method: "POST",
    });


    if (!response.ok) throw new Error("Failed to fetch chats");

    const data = await response.json();
    setAllCreatedChatsFunction([...data]);
    return data; 
  } catch (err) {
    console.error("Error fetching chats:", err);
  }

}

 

    


export  function removeValueFromArray(array,valueToRemove){

    return array.filter(item=>item!==valueToRemove)

}


