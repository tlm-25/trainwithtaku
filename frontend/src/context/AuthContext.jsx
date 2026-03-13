import { useState, useEffect, useContext, createContext } from "react";

//initialise context - create context object - allow to share data globally across components without passing props manually
const AuthContext = createContext()

//create custom react hook from which we can destructure any of these values
//returns context's value - don't need to import useContext and AuthContext everywhere  
export function useAuth() {
    return useContext(AuthContext)
}


//wrapper component to place at top level of react app (in index.js or App.js) - holds state of logged in user
export function AuthProvider(props){
    //destructure chidren from the props - wrapper for everythin in app, supplies auth state
    const {children} = props
    //state for user 
    const [globalUser, setGlobalUser] = useState(null);


    const [isLoading,setIsLoading] = useState(false);

   
    async function signUp(email,password,userType,confirmPassword) {

        const response = await fetch(`http://localhost:8000/add_user`,{
            method: 'POST',
            headers: {
                "Content-Type":"application/json"
            },
            body: JSON.stringify({
                
                email:email,
                password:password,
                user_type:userType,
                confirm_password:confirmPassword})

            })

            const data = await response.json()
            console.log(data)
            

                return {message: data.message,
                        status: response.status

                }


    
            
    }


    // authenticate a user trying to log in
    async function  login(email,password) {

        const response = await fetch("http://127.0.0.1:8000/login_with_access_token", {
        method: "POST",
        credentials: "include",
        headers: {
            //expected content type for the fastapi endpoint with Oauth form authentication - use URLSearchParams to format body content as form data
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body: new URLSearchParams({
            
            username: email,   
            password: password
        })
    });

        if (response.ok) {
            console.log(response)
            //if user enters correct credentials, set the global user state using the access token to give the user access to resources
            const data = await response.json()
            setGlobalUser({ email:email, token: data.access_token })
            return {
                status: response.status,
                message: data.message
            }

        }

        else {

            //if user enters incorrect credentials, simply return the message (which will indicate that they input invalid credentials)
            const data = await response.json()
            
            return {status: response.status,
                    message: data.message
                }


        }

        
        
    }


    async function logout(){
        setGlobalUser(null)
    }


    //anything contained here becomes part of the gloabl state - accessible anywhere in application
    //anything in here is shared vis context
    const value = {globalUser, isLoading, signUp,login,logout}
    //takes two arguments - first is a callback function (function that runs when the event we are looking or is triggered)
    //second is a dependency array that contains (or doesn't contain) when this logic gets run
    //we leave dependency array empty, want this logic to run when the page loads for the first time
    useEffect(()=>{
        // check that user has a valid a
        async function checkAuth() {
            try {

                const response = await fetch("http://127.0.0.1:8000/me",{
                    method: "GET",
                    credentials: "include"
                })

                if(response.ok){
                    const data = await response.json()
                    console.log(data)
                    //store the authenticated user in the global state - allow the rest of the app to know that the user has logged in 
                    setGlobalUser(data)
                } else {
                    //if response gives an error- user is not authenticated, clear any exisiting user state
                    setGlobalUser(null)
                }


            }

            catch (error) {
                //if something fails (e.g. if the server is down, or there is a network error)
                //we assume that the user is not authenticated
                console.error("Auth check failed",error)
                setGlobalUser(null)

            }

        }

        //invoke the authentication check 
        checkAuth()



    
    },[])


    return (

        //provde value to all components in provider - available to all children

        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>


    )






} 