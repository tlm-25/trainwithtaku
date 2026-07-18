import toast from "react-hot-toast";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useState } from "react";
import { BASE_URL } from "../api";
function ResetPasswordForm(){
    const [newPasswordInput,setNewPasswordInput] = useState("");
    const [confirmNewPasswordInput,setConfirmNewPasswordInput] = useState("");
    //redirect 
    // new instance of 
    const [searchParams] =  useSearchParams();

    // get the 'token?=' portion of the url for the password reset
    const resetToken = searchParams.get("token")

    const navigate = useNavigate()




    const handleNewPasswordInputChange = async (event) =>{
        event.preventDefault()
        const value = event.target.value;
        setNewPasswordInput(value)
        setPasswordValidation({
            //conditions for password to be valid 
            hasLowerCase: hasLowerCase(value),
            hasUpperCase: hasUpperCase(value),
            hasNumber: hasNumber(value),
            hasSpecialCharacters: hasSpecialCharacters(value),
            hasEightCharacters: hasEightCharacters(value)
        });
        

    }


        const [passwordValidation, setPasswordValidation] = useState({
            hasLowerCase: false,
            hasUpperCase: false,
            hasNumber: false,
            hasSpecialCharacters: false,
            hasEightCharacters: false
        });



    const handleConfirmNewPasswordInputChange = async (event) =>{
        event.preventDefault()
        setConfirmNewPasswordInput(event.target.value)
    }


    // Track conditions for password


    //Password check 
    const hasLowerCase = (str) => /[a-z]/.test(str);
    const hasUpperCase = (str) => /[A-Z]/.test(str);
    const hasNumber = (str) => /\d/.test(str);
    const hasEightCharacters = (str) => str.length >= 8
    const hasSpecialCharacters = (str) => /[-+_!@#$%^&*.,?]/.test(str);
    // check that password meets valid criteria
    const passwordValid = passwordValidation.hasLowerCase && passwordValidation.hasUpperCase && passwordValidation.hasSpecialCharacters && passwordValidation.hasNumber && (newPasswordInput==confirmNewPasswordInput)




    const handleSubmitNewPassword = async (event) => {
        event.preventDefault()

        alert("This link is one-time use. Request a new link if you need to reset again."); 

        
        console.log(resetToken)

        const response = await fetch(`${BASE_URL}/api/reset_password`,{
            method: "POST",
            body: JSON.stringify({

                "token":resetToken,
                "new_password":newPasswordInput,
                "confirm_new_password":confirmNewPasswordInput


            }),


            headers: {
                "Content-Type":"application/json"

            }
        
        
    
        })

        const data = await response.json()

        if (response.ok){
            //display success message
            toast.success('password successfully reset')
            setNewPasswordInput("")
            setConfirmNewPasswordInput("")

            //redirect to homepage
            navigate("/")
            
        }
        else if (response.status==401){
            //if token has expired or is invalid
            toast.error(data.detail)


        }

        else {
            toast.error(data.message)
        }


    }






    return (
        <>
        
        
       
       
        <form type="submit" onSubmit={handleSubmitNewPassword} className="password-reset">
            <p className="forgot-password-form-header">
                Enter the email you used to create TWT Fitness account, then confirm your password 
                

                
   
                
                
            </p>
            <p >IMPORTANT: The link expires after 20mins. Also, If you have any previous reset links, they will no longer work. Use the latest link.</p>

            <input type="password" value={newPasswordInput} placeholder="Enter your new password" onChange={handleNewPasswordInputChange}/>
            <input type="password" value={confirmNewPasswordInput} placeholder="confirm your new password" onChange={handleConfirmNewPasswordInputChange}/>
            <button type="submit" disabled={!passwordValid} className="reset-password-button">Reset password</button>
        </form>
            

        </>

)



}

export default ResetPasswordForm; 