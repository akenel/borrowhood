<#import "template.ftl" as layout>
<@layout.emailLayout>
  <h1 style="font-size:22px; margin:0 0 14px; color:#222222;">Confirm your email</h1>
  <p style="font-size:15px; line-height:1.6; margin:0; color:#444444;">
    Almost there. Click below to confirm this is your email address for your Banco account.
  </p>
  <table role="presentation" cellpadding="0" cellspacing="0" style="margin:28px 0;">
    <tr>
      <td align="center" bgcolor="#8B0000" style="border-radius:8px;">
        <a href="${link}" target="_blank" style="display:inline-block; padding:16px 42px; font-size:17px; font-weight:bold; color:#ffffff; text-decoration:none; border-radius:8px;">Confirm my email &rarr;</a>
      </td>
    </tr>
  </table>
  <p style="font-size:13px; line-height:1.6; color:#888888; margin:0;">
    Button not working? Copy this link into your browser:<br>
    <a href="${link}" style="color:#8B0000; word-break:break-all;">${link}</a>
  </p>
</@layout.emailLayout>
