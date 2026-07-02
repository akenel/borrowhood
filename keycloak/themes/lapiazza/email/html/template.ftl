<#macro emailLayout>
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin:0; padding:0; background:#f4f4f4; font-family:Arial, Helvetica, sans-serif; color:#222222;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f4f4f4; padding:24px 0;">
    <tr>
      <td align="center">
        <table role="presentation" width="480" cellpadding="0" cellspacing="0" style="width:480px; max-width:92%; background:#ffffff; border-radius:10px; overflow:hidden; border:1px solid #e6e6e6;">
          <!-- header: the wolf -->
          <tr>
            <td align="center" style="background:#8B0000; padding:28px 24px 20px;">
              <img src="https://banco.lapiazza.app/static/lapiazza-wolf.png" width="72" height="72" alt="La Piazza" style="display:block; border:0; border-radius:10px; background:#ffffff;">
              <div style="color:#ffffff; font-size:20px; font-weight:bold; letter-spacing:1px; margin-top:12px;">La Piazza</div>
              <div style="color:#f2d6d6; font-size:12px; margin-top:2px;">Banco &middot; Point of Sale</div>
            </td>
          </tr>
          <!-- body -->
          <tr>
            <td style="padding:32px 32px 36px;">
              <#nested>
            </td>
          </tr>
          <!-- footer -->
          <tr>
            <td style="background:#faf7f7; border-top:1px solid #eeeeee; padding:18px 32px; color:#999999; font-size:12px; line-height:1.5;">
              La Piazza &middot; Trapani, Sicilia<br>
              You got this because someone asked for it on your Banco account. If it wasn&rsquo;t you, just ignore this email &mdash; nothing changes.
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
</#macro>
