import { useState } from "react"
import toast from "react-hot-toast";
import { BASE_URL } from "../api";


function ForgotPasswordForm(){

    const [emailInput,setEmailInput] = useState("");


    //valid email address
    const emailValid = (emailInput && /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}$/i.test(emailInput))


    const handleEmailInputCHange = async (event) => {
        event.preventDefault();
        setEmailInput(event.target.value)

        


        

        
    }





    const requestPasswordResetLink = async (event) => {
        event.preventDefault();

        const response = await fetch(`${BASE_URL}/api/send_change_password_link`,{
            method: "POST",
            body: JSON.stringify({
                email: emailInput
            }),
            headers:{
                "Content-Type":"application/json"
            }
        }
        
        )
        const data = await response.json()
        const message = data.message


        if (response.ok){
                       
            toast.success(message);
            setEmailInput("");
        }
        else {
            toast.error(message);
            setEmailInput("");
        }
        



    }



    return (
        <>

        <form className="password-reset" onSubmit={requestPasswordResetLink}>
            
            <p className="forgot-password-form-header">
                Enter the email you used to create TWT Fitness account, then press <strong>'Send reset link.'</strong>   
                
                You'll be emailed a link to reset your password. 
                
   
                
                
            </p>
            <p >IMPORTANT: The link expires after 20mins. Also, If you have any previous reset links, they will no longer work. Use the latest link.</p>
            {!emailValid&&<p className="forgot-password-form-header">EMAIL ADDRESS MUST BE VALID FORMAT </p>}
            <input onChange={handleEmailInputCHange} value={emailInput} type="text" placeholder="Enter your email address"/>
            
            <button type="submit"  className="reset-password-button" disabled={!emailValid}>Send reset link</button>



        </form>        
        </>
    )
}


export default ForgotPasswordForm;